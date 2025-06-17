from typing import Optional, Tuple
from fastapi import Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.exceptions import APIException

# Configuración del rate limiter
limiter = Limiter(key_func=get_remote_address)

# Configuración de límites por ruta
RATE_LIMITS = {
    "default": "100/minute",
    "auth": "5/minute",
    "events": "50/minute",
    "orders": "20/minute"
}

def get_rate_limit(request: Request) -> str:
    """Obtiene el límite de rate para la ruta actual."""
    path = request.url.path
    
    if path.startswith("/api/v1/auth"):
        return RATE_LIMITS["auth"]
    elif path.startswith("/api/v1/events"):
        return RATE_LIMITS["events"]
    elif path.startswith("/api/v1/orders"):
        return RATE_LIMITS["orders"]
    
    return RATE_LIMITS["default"]

class RateLimitExceededException(APIException):
    """Excepción para cuando se excede el límite de rate."""
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=429,
            type="https://api.bipass.com/errors/rate-limit-exceeded",
            title="Rate Limit Exceeded",
            detail="Too many requests",
            additional_data={"retry_after": retry_after}
        )

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Manejador de excepciones para rate limit exceeded."""
    retry_after = int(exc.retry_after)
    raise RateLimitExceededException(retry_after=retry_after) 