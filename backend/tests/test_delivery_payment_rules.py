from test_api import client, as_user, book, request, accept, A, B


def create_transaction(client, kind='Satış'):
    b = book(client, kind)
    r = request(client, b['id'])
    return accept(client, r['id'])


def test_sale_delivery_requires_successful_demo_payment(client):
    tx = create_transaction(client)
    did = tx['deliveries'][0]['id']
    url = f'/api/deliveries/{did}'
    data = {'meeting_point': 'Kampüs kütüphanesi'}

    # Ödeme yoksa teslimat başlatılamaz.
    assert client.patch(url, json=data).status_code == 409

    as_user(B)
    payment_url = f'/api/transactions/{tx["id"]}/demo-payment'

    # Başarısız ödeme teslimatı açmaz.
    assert client.post(
        payment_url,
        json={'method': 'card', 'outcome': 'failed'}
    ).status_code == 201

    as_user(A)
    assert client.patch(url, json=data).status_code == 409

    # Başarılı demo ödeme teslimatı açar.
    as_user(B)
    assert client.post(
        payment_url,
        json={'method': 'card', 'outcome': 'success'}
    ).status_code == 201

    as_user(A)
    result = client.patch(url, json=data)
    assert result.status_code == 200, result.text
    assert result.json()['status'] == 'dispatched'


def test_sale_completion_requires_successful_demo_payment(client):
    tx = create_transaction(client)
    did = tx['deliveries'][0]['id']

    # Normal API üzerinden ödeme olmadan teslimat açılamaz.
    assert client.patch(
        f'/api/deliveries/{did}',
        json={'meeting_point': 'Kampüs'}
    ).status_code == 409

    # Önce başarılı demo ödeme oluştur.
    as_user(B)
    response = client.post(
        f'/api/transactions/{tx["id"]}/demo-payment',
        json={'method': 'transfer', 'outcome': 'success'}
    )
    assert response.status_code == 201, response.text

    as_user(A)
    assert client.patch(
        f'/api/deliveries/{did}',
        json={'meeting_point': 'Kampüs'}
    ).status_code == 200

    # Tek tarafın onayı işlemi tamamlamaz.
    response = client.post(f'/api/transactions/{tx["id"]}/confirm')
    assert response.status_code == 200
    assert response.json()['status'] == 'in_delivery'

    # İki tarafın onayı tamamlar.
    as_user(B)
    response = client.post(f'/api/transactions/{tx["id"]}/confirm')
    assert response.status_code == 200
    assert response.json()['status'] == 'completed'


def test_donation_delivery_does_not_require_payment(client):
    tx = create_transaction(client, 'Bağış')
    did = tx['deliveries'][0]['id']

    result = client.patch(
        f'/api/deliveries/{did}',
        json={'meeting_point': 'Kütüphane'}
    )
    assert result.status_code == 200, result.text


def test_sale_cannot_be_confirmed_without_payment_even_if_delivery_advanced(client):
    from sqlalchemy import select
    from sqlalchemy.orm import Session
    import main
    from models import Transaction, Delivery

    tx = create_transaction(client)

    # Test veritabanında teslimatın ilerlemiş olduğu durumu oluştur.
    # Bu işlem gerçek uygulama veritabanını değiştirmez.
    with Session(main.engine, expire_on_commit=False) as session:
        transaction = session.get(Transaction, tx['id'])
        delivery = session.scalar(
            select(Delivery).where(Delivery.transaction_id == tx['id'])
        )

        transaction.status = 'in_delivery'
        delivery.status = 'dispatched'
        delivery.meeting_point = 'Kampüs'

        session.commit()

    # Satıcı, ödeme olmadan işlemi onaylayamaz.
    as_user(A)
    response = client.post(f'/api/transactions/{tx["id"]}/confirm')
    assert response.status_code == 409, response.text

    # Alıcı da ödeme olmadan işlemi onaylayamaz.
    as_user(B)
    response = client.post(f'/api/transactions/{tx["id"]}/confirm')
    assert response.status_code == 409, response.text

    # Ödeme başarılı olduğunda onaylama mümkün olmalı.
    payment = client.post(
        f'/api/transactions/{tx["id"]}/demo-payment',
        json={'method': 'card', 'outcome': 'success'}
    )
    assert payment.status_code == 201, payment.text

    as_user(A)
    response = client.post(f'/api/transactions/{tx["id"]}/confirm')
    assert response.status_code == 200, response.text
    assert response.json()['status'] == 'in_delivery'

    as_user(B)
    response = client.post(f'/api/transactions/{tx["id"]}/confirm')
    assert response.status_code == 200, response.text
    assert response.json()['status'] == 'completed'
