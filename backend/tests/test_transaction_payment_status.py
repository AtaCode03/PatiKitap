from test_api import client, as_user, book, request, accept, A, B


def test_sale_payment_status_visible_to_both_parties(client):
    b = book(client, 'Satış')
    r = request(client, b['id'])
    tx = accept(client, r['id'])

    url = '/api/me/transactions'

    # Satıcı: henüz ödeme yok.
    as_user(A)
    assert client.get(url).json()[0]['demo_payment_status'] == 'pending'

    # Alıcı: henüz ödeme yok.
    as_user(B)
    assert client.get(url).json()[0]['demo_payment_status'] == 'pending'

    payment = client.post(
        f'/api/transactions/{tx["id"]}/demo-payment',
        json={'method': 'card', 'outcome': 'success'}
    )
    assert payment.status_code == 201, payment.text

    # Alıcı başarılı ödeme durumunu görür.
    assert client.get(url).json()[0]['demo_payment_status'] == 'success'

    # Satıcı da yalnızca ödeme durumunu görür.
    as_user(A)
    result = client.get(url)
    assert result.status_code == 200
    assert result.json()[0]['demo_payment_status'] == 'success'
    assert 'reference' not in result.json()[0]


def test_donation_has_no_demo_payment_status(client):
    b = book(client, 'Bağış')
    r = request(client, b['id'])
    accept(client, r['id'])

    as_user(A)
    assert client.get('/api/me/transactions').json()[0]['demo_payment_status'] is None
