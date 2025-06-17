from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.services.base import BaseService

class EventService(BaseService[Event, EventCreate, EventUpdate]):
    def __init__(self, db: Session):
        super().__init__(Event, db)

    def transform_to_response(self, event: Event) -> EventResponse:
        """
        Transforma la entidad Event de la base de datos a la respuesta de la API.
        Esta transformación incluye:
        1. Cálculo de disponibilidad de tickets
        2. Formateo de fechas
        3. Agregación de información del venue
        4. Cálculo de estadísticas de ventas
        """
        # Obtener información del venue
        venue = event.venue
        
        # Calcular estadísticas
        total_tickets_sold = sum(ticket.order.total_amount for ticket in event.tickets if ticket.status == "sold")
        average_rating = sum(review.rating for review in event.reviews) / len(event.reviews) if event.reviews else 0
        
        return EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            event_date=event.event_date.isoformat(),
            venue_name=venue.name if venue else None,
            venue_address=venue.address if venue else None,
            price=event.price,
            available_tickets=event.available_tickets,
            total_tickets_sold=total_tickets_sold,
            average_rating=round(average_rating, 2),
            created_at=event.created_at.isoformat(),
            updated_at=event.updated_at.isoformat()
        )

    def get_events_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        venue_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[EventResponse]:
        """
        Obtiene eventos con filtros aplicados y transforma los resultados.
        """
        query = self.db.query(Event)
        
        if venue_id:
            query = query.filter(Event.venue_id == venue_id)
        if min_price:
            query = query.filter(Event.price >= min_price)
        if max_price:
            query = query.filter(Event.price <= max_price)
        if start_date:
            query = query.filter(Event.event_date >= start_date)
        if end_date:
            query = query.filter(Event.event_date <= end_date)
            
        events = query.offset(skip).limit(limit).all()
        return [self.transform_to_response(event) for event in events] 