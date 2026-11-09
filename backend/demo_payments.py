"""PatiKitap demo payment rules. No real payment processing."""

from uuid import uuid4
from pydantic import BaseModel, ConfigDict
from typing import Literal
from fastapi import HTTPException

PaymentMethod = Literal["card", "transfer"]
PaymentOutcome = Literal["success", "failed", "cancelled"]


class DemoPaymentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    method: PaymentMethod
    outcome: PaymentOutcome


def validate_demo_sale(tx, user_id):
    if tx.requester_id != user_id:
        raise HTTPException(403, "Yalnızca alıcı demo ödeme yapabilir.")

    if tx.kind != "Satış":
        raise HTTPException(409, "Yalnızca satış işlemlerinde demo ödeme yapılabilir.")

    if tx.status not in ("accepted", "in_delivery"):
        raise HTTPException(409, "Bu işlem demo ödeme için uygun durumda değil.")

    values = (tx.price_cents, tx.support_cents, tx.fee_cents)

    if (
        any(type(v) is not int or v < 0 for v in values)
        or tx.price_cents <= 0
        or tx.support_cents + tx.fee_cents > tx.price_cents
    ):
        raise HTTPException(409, "Satış tutarları geçersiz.")

    return {
        "price_cents": tx.price_cents,
        "support_cents": tx.support_cents,
        "fee_cents": tx.fee_cents,
        "total_cents": tx.price_cents,
    }


def simulate_demo_payment(tx, user_id, data):
    amounts = validate_demo_sale(tx, user_id)

    return {
        "transaction_id": tx.id,
        "reference": f"DEMO-{tx.id}-{uuid4().hex[:12].upper()}",
        "method": data.method,
        "outcome": data.outcome,
        "mode": "simulation",
        "real_payment": False,
        **amounts,
    }
