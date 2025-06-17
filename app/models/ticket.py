from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum
from decimal import Decimal


class TicketType(str, Enum):
    VIP = "VIP"
    GENERAL = "General"
    STREAMING = "Streaming"


class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    type: TicketType
    price: Decimal = Field(decimal_places=2, max_digits=10)
    total_stock: int = Field(gt=0)
    available_stock: int = Field(ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    event: Optional["Event"] = Relationship(back_populates="tickets")
    order_items: List["OrderItem"] = Relationship(back_populates="ticket")