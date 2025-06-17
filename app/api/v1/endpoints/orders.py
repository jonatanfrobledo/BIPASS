from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from decimal import Decimal

from app.db.session import get_session
from app.models.order import Order, OrderItem, OrderStatus
from app.models.ticket import Ticket
from app.models.event import Event
from app.models.venue import Venue
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Create order
    order = Order(user_id=current_user.id)
    session.add(order)
    session.flush()  # Get order ID without committing
    
    total_amount = Decimal(0)
    venue_capacity_check = {}
    
    # Process each order item
    for item_data in order_data.order_items:
        ticket = session.get(Ticket, item_data.ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {item_data.ticket_id} not found"
            )
        
        # Check stock availability
        if ticket.available_stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for ticket {ticket.id}. Available: {ticket.available_stock}"
            )
        
        # Check venue capacity
        event = session.get(Event, ticket.event_id)
        venue = session.get(Venue, event.venue_id)
        
        if event.id not in venue_capacity_check:
            # Calculate total tickets already sold for this event
            statement = select(OrderItem).join(Ticket).where(
                Ticket.event_id == event.id,
                OrderItem.order_id.in_(
                    select(Order.id).where(Order.status != OrderStatus.CANCELLED)
                )
            )
            sold_items = session.exec(statement).all()
            total_sold = sum(item.quantity for item in sold_items)
            venue_capacity_check[event.id] = total_sold
        
        venue_capacity_check[event.id] += item_data.quantity
        
        if venue_capacity_check[event.id] > venue.total_capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order exceeds venue capacity for event {event.name}"
            )
        
        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            ticket_id=ticket.id,
            quantity=item_data.quantity,
            unit_price=ticket.price
        )
        session.add(order_item)
        
        # Update ticket stock
        ticket.available_stock -= item_data.quantity
        session.add(ticket)
        
        # Calculate total
        total_amount += ticket.price * item_data.quantity
    
    # Update order total
    order.total = total_amount
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order


@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Order).where(Order.user_id == current_user.id)
    orders = session.exec(statement).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


@router.put("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order"
        )
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel pending orders"
        )
    
    # Restore ticket stock
    for order_item in order.order_items:
        ticket = session.get(Ticket, order_item.ticket_id)
        ticket.available_stock += order_item.quantity
        session.add(ticket)
    
    # Update order status
    order.status = OrderStatus.CANCELLED
    session.add(order)
    session.commit()
    
    return {"message": "Order cancelled successfully"}