from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum
from decimal import Decimal


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total: Decimal = Field(decimal_places=2, max_digits=10, default=0)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")
    payments: List["Payment"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    ticket_id: int = Field(foreign_key="ticket.id")
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(decimal_places=2, max_digits=10)
    
    # Relationships
    order: Optional["Order"] = Relationship(back_populates="order_items")
    ticket: Optional["Ticket"] = Relationship(back_populates="order_items")
    