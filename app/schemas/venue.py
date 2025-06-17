from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VenueBase(BaseModel):
    name: str
    address: str
    total_capacity: int


class VenueCreate(VenueBase):
    pass


class VenueUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    total_capacity: Optional[int] = None


class VenueResponse(VenueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True