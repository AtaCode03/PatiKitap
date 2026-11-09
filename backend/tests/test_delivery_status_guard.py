from sqlalchemy import select
from sqlalchemy.orm import Session

import main
from models import Delivery
from test_api import client, as_user, book, request, accept, A, B


def test_cancelled_delivery_cannot_be_confirmed(client):
    b = book(client, 'Bağış')
    r = request(client, b['id'])
    tx = accept(client, r['id'])

    did = tx['deliveries'][0]['id']

    response = client.patch(
        f'/api/deliveries/{did}',
        json={'meeting_point': 'Kampüs kütüphanesi'}
    )
    assert response.status_code == 200, response.text

    with Session(main.engine, expire_on_commit=False) as session:
        delivery = session.scalar(
            select(Delivery).where(Delivery.id == did)
        )
        delivery.status = 'cancelled'
        session.commit()

    as_user(A)
    response = client.post(f'/api/transactions/{tx["id"]}/confirm')

    assert response.status_code == 409

    as_user(B)
    response = client.post(f'/api/transactions/{tx["id"]}/confirm')

    assert response.status_code == 409
