from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.db.session import get_session
from app.models.event import Event
from app.models.venue import Venue
from app.models.user import User
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.utils.dependencies import get_current_user, get_current_admin_user

router = APIRouter()


@router.post("/", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    # Validate venue exists
    venue = session.get(Venue, event_data.venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    # Validate dates
    if event_data.start_datetime >= event_data.end_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start datetime must be before end datetime"
        )
    
    event = Event(**event_data.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.get("/", response_model=List[EventResponse])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    statement = select(Event)
    
    if search:
        statement = statement.where(Event.name.contains(search))
    
    statement = statement.offset(skip).limit(limit)
    events = session.exec(statement).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_update: EventUpdate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    event_data = event_update.model_dump(exclude_unset=True)
    
    # Validate venue if being updated
    if "venue_id" in event_data:
        venue = session.get(Venue, event_data["venue_id"])
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found"
            )
    
    # Validate dates if being updated
    start_dt = event_data.get("start_datetime", event.start_datetime)
    end_dt = event_data.get("end_datetime", event.end_datetime)
    if start_dt >= end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start datetime must be before end datetime"
        )
    
    for field, value in event_data.items():
        setattr(event, field, value)
    
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    session.delete(event)
    session.commit()
    return {"message": "Event deleted successfully"}