from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    order_id: int
    amount: Decimal
    payment_method: PaymentMethod


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_date: datetime
    amount: Decimal
    payment_method: PaymentMethod
    status: PaymentStatus

    class Config:
        from_attributes = True