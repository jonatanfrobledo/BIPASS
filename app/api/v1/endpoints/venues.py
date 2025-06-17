from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.db.session import get_session
from app.models.venue import Venue
from app.models.user import User
from app.schemas.venue import VenueCreate, VenueResponse, VenueUpdate
from app.utils.dependencies import get_current_user, get_current_admin_user

router = APIRouter()


@router.post("/", response_model=VenueResponse)
async def create_venue(
    venue_data: VenueCreate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    venue = Venue(**venue_data.model_dump())
    session.add(venue)
    session.commit()
    session.refresh(venue)
    return venue


@router.get("/", response_model=List[VenueResponse])
async def get_venues(session: Session = Depends(get_session)):
    statement = select(Venue)
    venues = session.exec(statement).all()
    return venues


@router.get("/{venue_id}", response_model=VenueResponse)
async def get_venue(venue_id: int, session: Session = Depends(get_session)):
    venue = session.get(Venue, venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    return venue


@router.put("/{venue_id}", response_model=VenueResponse)
async def update_venue(
    venue_id: int,
    venue_update: VenueUpdate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    venue = session.get(Venue, venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    venue_data = venue_update.model_dump(exclude_unset=True)
    for field, value in venue_data.items():
        setattr(venue, field, value)
    
    session.add(venue)
    session.commit()
    session.refresh(venue)
    return venue


@router.delete("/{venue_id}")
async def delete_venue(
    venue_id: int,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    venue = session.get(Venue, venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    session.delete(venue)
    session.commit()
    return {"message": "Venue deleted successfully"}