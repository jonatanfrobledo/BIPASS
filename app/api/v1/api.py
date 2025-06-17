"""
API router configuration.
"""
from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.venues import router as venues_router
from app.api.v1.endpoints.events import router as events_router
from app.api.v1.endpoints.tickets import router as tickets_router
from app.api.v1.endpoints.orders import router as orders_router
from app.api.v1.endpoints.payments import router as payments_router
from app.api.v1.endpoints.reviews import router as reviews_router
from app.api.v1.endpoints.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(venues_router, prefix="/venues", tags=["Venues"])
api_router.include_router(events_router, prefix="/events", tags=["Events"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(orders_router, prefix="/orders", tags=["Orders"])
api_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"]) 