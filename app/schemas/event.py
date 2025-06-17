from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EventBase(BaseModel):
    name: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    venue_id: int


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    venue_id: Optional[int] = None


class EventResponse(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True