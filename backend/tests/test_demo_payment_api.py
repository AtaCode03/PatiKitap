from test_api import client, as_user, book, request, accept, A, B


def create_sale(client):
    b = book(client, 'Satış')
    r = request(client, b['id'])
    tx = accept(client, r['id'])
    return tx


def test_payment_is_saved_and_visible_to_buyer(client):
    tx = create_sale(client)
    as_user(B)

    response = client.post(
        f'/api/transactions/{tx["id"]}/demo-payment',
        json={'method': 'card', 'outcome': 'success'}
    )

    assert response.status_code == 201, response.text
    payment = response.json()

    assert payment['total_cents'] == 10000
    assert payment['support_cents'] == 2000
    assert payment['real_payment'] is False

    history = client.get('/api/me/demo-payments')
    assert history.status_code == 200
    assert len(history.json()) == 1

    detail = client.get(f'/api/demo-payments/{payment["id"]}')
    assert detail.status_code == 200
    assert detail.json()['reference'] == payment['reference']


def test_duplicate_success_is_rejected(client):
    tx = create_sale(client)
    as_user(B)

    url = f'/api/transactions/{tx["id"]}/demo-payment'
    payload = {'method': 'card', 'outcome': 'success'}

    assert client.post(url, json=payload).status_code == 201
    assert client.post(url, json=payload).status_code == 409


def test_failed_payment_can_be_retried(client):
    tx = create_sale(client)
    as_user(B)

    url = f'/api/transactions/{tx["id"]}/demo-payment'

    assert client.post(
        url, json={'method': 'card', 'outcome': 'failed'}
    ).status_code == 201

    assert client.post(
        url, json={'method': 'transfer', 'outcome': 'success'}
    ).status_code == 201

    history = client.get('/api/me/demo-payments').json()
    assert len(history) == 2


def test_seller_cannot_pay_or_read_buyer_history(client):
    tx = create_sale(client)
    as_user(A)

    response = client.post(
        f'/api/transactions/{tx["id"]}/demo-payment',
        json={'method': 'card', 'outcome': 'success'}
    )
    assert response.status_code == 403
    assert client.get('/api/me/demo-payments').json() == []


def test_buyer_receipt_is_private(client):
    tx = create_sale(client)
    as_user(B)

    payment = client.post(
        f'/api/transactions/{tx["id"]}/demo-payment',
        json={'method': 'card', 'outcome': 'success'}
    ).json()

    as_user(A)
    assert client.get(
        f'/api/demo-payments/{payment["id"]}'
    ).status_code == 403


def test_donation_cannot_be_paid(client):
    b = book(client, 'Bağış')
    r = request(client, b['id'])
    tx = accept(client, r['id'])

    as_user(B)
    response = client.post(
        f'/api/transactions/{tx["id"]}/demo-payment',
        json={'method': 'card', 'outcome': 'success'}
    )
    assert response.status_code == 409
