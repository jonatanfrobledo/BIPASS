from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal
from app.models.ticket import TicketType


class TicketBase(BaseModel):
    event_id: int
    type: TicketType
    price: Decimal
    total_stock: int


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    type: Optional[TicketType] = None
    price: Optional[Decimal] = None
    total_stock: Optional[int] = None


class TicketResponse(TicketBase):
    id: int
    available_stock: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True