from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List

from app.db.session import get_session
from app.models.ticket import Ticket
from app.models.event import Event
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.utils.dependencies import get_current_user, get_current_admin_user

router = APIRouter()


@router.post("/", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    # Validate event exists
    event = session.get(Event, ticket_data.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    ticket = Ticket(
        **ticket_data.model_dump(),
        available_stock=ticket_data.total_stock
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.get("/", response_model=List[TicketResponse])
async def get_tickets(
    event_id: int = Query(None),
    session: Session = Depends(get_session)
):
    statement = select(Ticket)
    
    if event_id:
        statement = statement.where(Ticket.event_id == event_id)
    
    tickets = session.exec(statement).all()
    return tickets


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, session: Session = Depends(get_session)):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    ticket_data = ticket_update.model_dump(exclude_unset=True)
    
    # Update available stock if total stock is being updated
    if "total_stock" in ticket_data:
        sold_tickets = ticket.total_stock - ticket.available_stock
        new_available = ticket_data["total_stock"] - sold_tickets
        if new_available < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reduce total stock below sold tickets"
            )
        ticket.available_stock = new_available
    
    for field, value in ticket_data.items():
        setattr(ticket, field, value)
    
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check if ticket has been sold
    if ticket.available_stock < ticket.total_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete ticket that has been sold"
        )
    
    session.delete(ticket)
    session.commit()
    return {"message": "Ticket deleted successfully"}