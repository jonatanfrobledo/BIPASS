from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import Dict, Any, List
from decimal import Decimal

from app.db.session import get_session
from app.models.user import User
from app.models.event import Event
from app.models.order import Order, OrderItem, OrderStatus
from app.models.ticket import Ticket
from app.models.payment import Payment, PaymentStatus
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
async def get_admin_stats(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    # Total users
    total_users = session.exec(select(func.count(User.id))).first()
    
    # Total events
    total_events = session.exec(select(func.count(Event.id))).first()
    
    # Total orders
    total_orders = session.exec(select(func.count(Order.id))).first()
    
    # Total revenue
    revenue_result = session.exec(
        select(func.sum(Payment.amount)).where(
            Payment.status == PaymentStatus.CONFIRMED
        )
    ).first()
    total_revenue = revenue_result or Decimal(0)
    
    # Tickets sold by event
    tickets_by_event = session.exec(
        select(
            Event.name,
            func.sum(OrderItem.quantity).label("tickets_sold")
        )
        .join(Ticket, Event.id == Ticket.event_id)
        .join(OrderItem, Ticket.id == OrderItem.ticket_id)
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.status == OrderStatus.PAID)
        .group_by(Event.id, Event.name)
    ).all()
    
    # Revenue by event
    revenue_by_event = session.exec(
        select(
            Event.name,
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue")
        )
        .join(Ticket, Event.id == Ticket.event_id)
        .join(OrderItem, Ticket.id == OrderItem.ticket_id)
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.status == OrderStatus.PAID)
        .group_by(Event.id, Event.name)
    ).all()
    
    return {
        "total_users": total_users,
        "total_events": total_events,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "tickets_by_event": [
            {"event_name": row[0], "tickets_sold": row[1]}
            for row in tickets_by_event
        ],
        "revenue_by_event": [
            {"event_name": row[0], "revenue": float(row[1])}
            for row in revenue_by_event
        ]
    }


@router.get("/orders")
async def get_all_orders(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    statement = select(Order)
    orders = session.exec(statement).all()
    return orders


@router.get("/payments")
async def get_all_payments(
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    statement = select(Payment)
    payments = session.exec(statement).all()
    return payments