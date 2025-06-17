from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    start_datetime: datetime
    end_datetime: datetime
    venue_id: int = Field(foreign_key="venue.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    venue: Optional["Venue"] = Relationship(back_populates="events")
    tickets: List["Ticket"] = Relationship(back_populates="event")
    reviews: List["Review"] = Relationship(back_populates="event")