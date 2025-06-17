from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    ticket_id: int
    quantity: int


class OrderItemResponse(BaseModel):
    id: int
    ticket_id: int
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    order_items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: OrderStatus
    total: Decimal
    order_items: List[OrderItemResponse]

    class Config:
        from_attributes = True