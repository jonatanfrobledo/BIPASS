from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional


class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="reviews")
    event: Optional["Event"] = Relationship(back_populates="reviews")