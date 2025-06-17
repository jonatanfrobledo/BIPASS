from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.db.session import get_session
from app.models.review import Review
from app.models.event import Event
from app.models.order import Order, OrderStatus
from app.models.order import OrderItem
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Validate event exists
    event = session.get(Event, review_data.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if event has ended
    if event.end_datetime > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot review an event that hasn't ended yet"
        )
    
    # Check if user has purchased tickets for this event
    statement = select(OrderItem).join(Ticket).join(Order).where(
        Ticket.event_id == review_data.event_id,
        Order.user_id == current_user.id,
        Order.status == OrderStatus.PAID
    )
    order_item = session.exec(statement).first()
    
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review events you have attended"
        )
    
    # Check if user has already reviewed this event
    statement = select(Review).where(
        Review.user_id == current_user.id,
        Review.event_id == review_data.event_id
    )
    existing_review = session.exec(statement).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this event"
        )
    
    # Create review
    review = Review(
        user_id=current_user.id,
        **review_data.model_dump()
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    
    return review


@router.get("/", response_model=List[ReviewResponse])
async def get_reviews(
    event_id: int = Query(None),
    session: Session = Depends(get_session)
):
    statement = select(Review)
    
    if event_id:
        statement = statement.where(Review.event_id == event_id)
    
    reviews = session.exec(statement).all()
    return reviews


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    return review


@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this review"
        )
    
    session.delete(review)
    session.commit()
    return {"message": "Review deleted successfully"}