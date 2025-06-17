from typing import Any, Optional, Callable
from functools import wraps
import json
from datetime import datetime, timedelta
from fastapi import Request
from redis import Redis
from app.core.config import get_settings

settings = get_settings()
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

def cache(
    expire: int = 300,  # 5 minutos por defecto
    key_prefix: str = "cache",
    include_user: bool = False
):
    """
    Decorador para cachear resultados de funciones.
    
    Args:
        expire: Tiempo de expiración en segundos
        key_prefix: Prefijo para la clave del caché
        include_user: Si se debe incluir el ID del usuario en la clave
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Construir la clave del caché
            cache_key_parts = [key_prefix, func.__name__]
            
            # Incluir argumentos en la clave
            if args:
                cache_key_parts.extend([str(arg) for arg in args])
            if kwargs:
                cache_key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            
            # Incluir usuario si es necesario
            if include_user and "request" in kwargs:
                request: Request = kwargs["request"]
                if hasattr(request.state, "user"):
                    cache_key_parts.append(f"user:{request.state.user.id}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Intentar obtener del caché
            cached_value = redis_client.get(cache_key)
            if cached_value:
                return json.loads(cached_value)
            
            # Si no está en caché, ejecutar la función
            result = await func(*args, **kwargs)
            
            # Guardar en caché
            redis_client.setex(
                cache_key,
                expire,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """
    Invalida todas las claves de caché que coincidan con el patrón.
    
    Args:
        pattern: Patrón de clave a invalidar (ej: "cache:get_events:*")
    """
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)

class CacheManager:
    """Clase para gestionar el caché de manera centralizada."""
    
    @staticmethod
    def get_event_cache_key(event_id: int) -> str:
        return f"cache:get_event:{event_id}"
    
    @staticmethod
    def get_events_list_cache_key(
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> str:
        key_parts = ["cache:get_events", f"skip:{skip}", f"limit:{limit}"]
        if filters:
            key_parts.extend([f"{k}:{v}" for k, v in sorted(filters.items())])
        return ":".join(key_parts)
    
    @staticmethod
    def invalidate_event_cache(event_id: int):
        """Invalida el caché de un evento específico."""
        invalidate_cache(f"cache:get_event:{event_id}")
        invalidate_cache("cache:get_events:*")
    
    @staticmethod
    def invalidate_all_events_cache():
        """Invalida todo el caché relacionado con eventos."""
        invalidate_cache("cache:get_events:*")
        invalidate_cache("cache:get_event:*") 