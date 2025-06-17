from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import structlog
import uuid
from typing import Callable
import time
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from app.core.config import get_settings

settings = get_settings()

# Configurar el logger global
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Obtener el ID de correlación del header o generar uno nuevo
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        
        # Agregar el ID de correlación al contexto de la request
        request.state.correlation_id = correlation_id
        
        # Procesar la request
        response = await call_next(request)
        
        # Agregar el ID de correlación al header de la respuesta
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Obtener el ID de correlación
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
        
        # Log de inicio de la request
        self.logger.info(
            "request_started",
            method=request.method,
            url=str(request.url),
            correlation_id=correlation_id
        )
        
        try:
            # Procesar la request
            response = await call_next(request)
            
            # Log de fin de la request
            self.logger.info(
                "request_finished",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                correlation_id=correlation_id
            )
            
            return response
            
        except Exception as e:
            # Log de error
            self.logger.error(
                "request_failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                correlation_id=correlation_id
            )
            raise

def setup_middleware(app):
    # Add CORS first
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request ID tracking
    app.add_middleware(RequestIDMiddleware)
    
    # Add correlation ID tracking
    app.add_middleware(CorrelationIdMiddleware)
    
    # Add structured logging
    app.add_middleware(LoggingMiddleware)
    
    # Add rate limiting last
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware) 