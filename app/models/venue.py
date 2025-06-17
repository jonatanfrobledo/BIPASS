from asyncio import Event
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


class Venue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    address: str = Field(max_length=500)
    total_capacity: int = Field(gt=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    events: List["Event"] = Relationship(back_populates="venue")