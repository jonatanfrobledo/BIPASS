from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from enum import Enum
from decimal import Decimal


class PaymentMethod(str, Enum):
    CARD = "card"
    TRANSFER = "transfer"
    CASH = "cash"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    amount: Decimal = Field(decimal_places=2, max_digits=10)
    payment_method: PaymentMethod
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    
    # Relationships
    order: Optional["Order"] = Relationship(back_populates="payments")