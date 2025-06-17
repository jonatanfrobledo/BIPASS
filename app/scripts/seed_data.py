#!/usr/bin/env python3
"""
Script to seed the database with sample data
"""

import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from datetime import datetime, timedelta
from decimal import Decimal

from app.db.session import engine
from app.models.venue import Venue
from app.models.event import Event
from app.models.ticket import Ticket, TicketType


def seed_data():
    """Seed the database with sample data"""
    with Session(engine) as session:
        # Create venues
        venues = [
            Venue(
                name="Teatro Nacional",
                address="Av. Principal 123, Ciudad",
                total_capacity=500
            ),
            Venue(
                name="Estadio Central",
                address="Calle Deportiva 456, Ciudad",
                total_capacity=10000
            ),
            Venue(
                name="Centro de Convenciones",
                address="Plaza Mayor 789, Ciudad",
                total_capacity=2000
            )
        ]
        
        for venue in venues:
            session.add(venue)
        session.commit()
        
        # Create events
        base_date = datetime.utcnow() + timedelta(days=30)
        
        events = [
            Event(
                name="Concierto de Rock Nacional",
                description="Los mejores grupos de rock del país en una noche inolvidable",
                start_datetime=base_date,
                end_datetime=base_date + timedelta(hours=4),
                venue_id=venues[0].id
            ),
            Event(
                name="Festival de Música Electrónica",
                description="Los mejores DJs internacionales en un festival épico",
                start_datetime=base_date + timedelta(days=15),
                end_datetime=base_date + timedelta(days=15, hours=8),
                venue_id=venues[1].id
            ),
            Event(
                name="Conferencia Tech 2024",
                description="Las últimas tendencias en tecnología y desarrollo",
                start_datetime=base_date + timedelta(days=45),
                end_datetime=base_date + timedelta(days=45, hours=6),
                venue_id=venues[2].id
            )
        ]
        
        for event in events:
            session.add(event)
        session.commit()
        
        # Create tickets for each event
        tickets_data = [
            # Concierto de Rock
            [
                (TicketType.GENERAL, Decimal("75.00"), 300),
                (TicketType.VIP, Decimal("150.00"), 100),
                (TicketType.STREAMING, Decimal("25.00"), 1000)
            ],
            # Festival Electrónica
            [
                (TicketType.GENERAL, Decimal("120.00"), 8000),
                (TicketType.VIP, Decimal("300.00"), 500),
                (TicketType.STREAMING, Decimal("40.00"), 2000)
            ],
            # Conferencia Tech
            [
                (TicketType.GENERAL, Decimal("200.00"), 1500),
                (TicketType.VIP, Decimal("400.00"), 200),
                (TicketType.STREAMING, Decimal("50.00"), 5000)
            ]
        ]
        
        for i, event in enumerate(events):
            for ticket_type, price, stock in tickets_data[i]:
                ticket = Ticket(
                    event_id=event.id,
                    type=ticket_type,
                    price=price,
                    total_stock=stock,
                    available_stock=stock
                )
                session.add(ticket)
        
        session.commit()
        print("Sample data seeded successfully!")
        print(f"Created {len(venues)} venues")
        print(f"Created {len(events)} events")
        print("Created tickets for all events")


if __name__ == "__main__":
    seed_data()