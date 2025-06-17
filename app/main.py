from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import traceback
import logging
from dotenv import load_dotenv
# Comentamos las importaciones de monitoreo para desarrollo
# from prometheus_client import make_asgi_app
# import sentry_sdk
# from sentry_sdk.integrations.fastapi import FastApiIntegration

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Cargar variables de entorno primero
load_dotenv()

from app.core.config import get_settings
from app.db.session import create_db_and_tables
from app.core.middleware import setup_middleware, CorrelationIdMiddleware, LoggingMiddleware
from app.core.exceptions import APIException
from app.api.v1.api import api_router

settings = get_settings()

# Inicializar Sentry solo en producción
# Comentamos la inicialización de Sentry para desarrollo
"""
if settings.ENVIRONMENT == "production":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
    )
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor del ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    try:
        # Inicio: Crear tablas de la base de datos
        create_db_and_tables()
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Crear la aplicación FastAPI con configuración básica
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}  # Mejora la visualización de Swagger
)

# Agregar middlewares
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar métricas de Prometheus
# Comentamos la configuración de Prometheus para desarrollo
"""
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
"""

# Incluir el router principal de la API
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """
    Endpoint raíz que muestra información básica de la API.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs_url": f"{settings.API_V1_STR}/docs",
        "redoc_url": f"{settings.API_V1_STR}/redoc"
    }

@app.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud de la aplicación.
    Útil para monitoreo y balanceo de carga.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/version")
async def version():
    """Endpoint para obtener la versión de la aplicación."""
    return {
        "version": settings.APP_VERSION
    }

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Manejador global de excepciones de la API."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.problem_detail.dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejador global de excepciones no controladas."""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    # Configuración para ejecutar la aplicación directamente
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.ENVIRONMENT == "development"  # Recarga automática en desarrollo
    )