from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import redis

# Obtener la ruta del directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Cargar variables de entorno desde .env
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Configuración básica
    APP_NAME: str = "BIPASS API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Base de datos
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "bipass_db")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    # Redis (deshabilitado por ahora)
    REDIS_ENABLED: bool = False
    
    # Rate limiting (deshabilitado por ahora)
    RATE_LIMIT_ENABLED: bool = False
    
    # Caché (deshabilitado por ahora)
    CACHE_ENABLED: bool = False
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"Database URL: {self.DATABASE_URL}")
        
        if self.REDIS_ENABLED:
            logger.info("Redis is enabled but not configured")
        else:
            logger.info("Redis is disabled")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

@lru_cache()
def get_settings() -> Settings:
    try:
        settings = Settings()
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        raise

settings = get_settings() 