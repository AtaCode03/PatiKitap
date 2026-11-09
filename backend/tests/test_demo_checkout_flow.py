"""PatiKitap demo checkout integration tests using the existing test DB."""

from test_api import client, as_user, book, request, accept, A, B


def test_complete_demo_checkout_flow(client):
    # 1. Satıcı kitap ilanı oluşturur.
    listing = book(client, 'Satış')

    # 2. Alıcı satış talebinde bulunur.
    req = request(client, listing['id'], who=B)

    # 3. Satıcı talebi kabul eder.
    tx = accept(client, req['id'], owner=A)
    tid = tx['id']

    assert tx['kind'] == 'Satış'
    assert tx['status'] == 'accepted'
    assert tx['price_cents'] == 10000
    assert tx['support_cents'] == 2000

    # 4. Alıcı önce başarısız demo ödeme dener.
    as_user(B)
    url = f'/api/transactions/{tid}/demo-payment'

    failed = client.post(
        url,
        json={'method': 'card', 'outcome': 'failed'}
    )

    assert failed.status_code == 201, failed.text
    assert failed.json()['outcome'] == 'failed'
    assert failed.json()['real_payment'] is False

    # 5. Alıcı başka yöntemle yeniden dener.
    success = client.post(
        url,
        json={'method': 'transfer', 'outcome': 'success'}
    )

    assert success.status_code == 201, success.text

    payment = success.json()

    assert payment['outcome'] == 'success'
    assert payment['method'] == 'transfer'
    assert payment['price_cents'] == 10000
    assert payment['support_cents'] == 2000
    assert payment['fee_cents'] == 0
    assert payment['total_cents'] == 10000
    assert payment['real_payment'] is False
    assert payment['reference'].startswith('DEMO-')

    # 6. Geçmişte her iki ödeme denemesi bulunur.
    history_response = client.get('/api/me/demo-payments')

    assert history_response.status_code == 200
    history = history_response.json()

    related = [
        item for item in history
        if item['transaction_id'] == tid
    ]

    assert len(related) == 2
    assert {item['outcome'] for item in related} == {
        'failed', 'success'
    }

    # 7. Dekont API'si kaydedilen verileri döndürür.
    receipt_response = client.get(
        f'/api/demo-payments/{payment["id"]}'
    )

    assert receipt_response.status_code == 200

    receipt = receipt_response.json()

    assert receipt['reference'] == payment['reference']
    assert receipt['total_cents'] == 10000
    assert receipt['buyer_id'] == B

    # 8. Aynı satış için ikinci başarılı ödeme engellenir.
    duplicate = client.post(
        url,
        json={'method': 'card', 'outcome': 'success'}
    )

    assert duplicate.status_code == 409

    # 9. Satıcı alıcının dekontunu göremez.
    as_user(A)

    forbidden = client.get(
        f'/api/demo-payments/{payment["id"]}'
    )

    assert forbidden.status_code == 403

    # 10. Demo ödeme, teslimatı otomatik tamamlamaz.
    as_user(B)
    transactions = client.get('/api/me/transactions')

    assert transactions.status_code == 200

    current = next(
        item for item in transactions.json()
        if item['id'] == tid
    )

    assert current['status'] == 'accepted'
    assert current['requester_confirmed'] is False
    assert current['owner_confirmed'] is False
