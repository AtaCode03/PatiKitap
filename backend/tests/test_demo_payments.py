from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from demo_payments import (
    DemoPaymentInput,
    simulate_demo_payment,
    validate_demo_sale,
)


def sale(**changes):
    data = {
        "id": 9001,
        "requester_id": "buyer",
        "kind": "Satış",
        "status": "accepted",
        "price_cents": 20000,
        "support_cents": 4000,
        "fee_cents": 0,
    }
    data.update(changes)
    return SimpleNamespace(**data)


def test_support_is_included_in_price():
    amounts = validate_demo_sale(sale(), "buyer")
    assert amounts["total_cents"] == 20000
    assert amounts["support_cents"] == 4000


def test_seller_cannot_pay():
    with pytest.raises(HTTPException) as error:
        validate_demo_sale(sale(), "seller")
    assert error.value.status_code == 403


@pytest.mark.parametrize("kind", ["Bağış", "Takas"])
def test_non_sale_rejected(kind):
    with pytest.raises(HTTPException) as error:
        validate_demo_sale(sale(kind=kind), "buyer")
    assert error.value.status_code == 409


@pytest.mark.parametrize("status", ["completed", "cancelled", "disputed"])
def test_closed_or_disputed_sale_rejected(status):
    with pytest.raises(HTTPException) as error:
        validate_demo_sale(sale(status=status), "buyer")
    assert error.value.status_code == 409


def test_backend_returns_demo_result():
    result = simulate_demo_payment(
        sale(), "buyer",
        DemoPaymentInput(method="card", outcome="success"),
    )
    assert result["outcome"] == "success"
    assert result["real_payment"] is False
    assert result["total_cents"] == 20000
    assert result["reference"].startswith("DEMO-9001-")


def test_invalid_amounts_rejected():
    with pytest.raises(HTTPException):
        validate_demo_sale(sale(support_cents=25000), "buyer")


def test_invalid_payment_method_rejected():
    with pytest.raises(ValueError):
        DemoPaymentInput(method="unknown", outcome="success")
