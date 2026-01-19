"""
Redis Adapter - Implementación de CacheService

Cumplimiento SOLID:
- Single Responsibility: Solo maneja operaciones de caché
- Dependency Inversion: Implementa interface CacheService
- Open/Closed: Extensible sin modificar código existente

Nota del desarrollador (María Gutiérrez):
Extraído de adapters.py para mejor organización.
Usa redis.asyncio para operaciones asíncronas reales.
"""
from typing import Optional
import json
import redis.asyncio as redis_async

from src.application.interfaces import CacheService


class RedisAdapter(CacheService):
    """
    Adaptador de Redis que implementa CacheService
    
    Usa redis.asyncio para operaciones asíncronas reales
    """

    def __init__(self, connection_string: str, ttl: int) -> None:
        """
        Inicializa el adaptador de Redis
        
        Args:
            connection_string: URL de conexión a Redis
            ttl: Tiempo de vida por defecto en segundos
        """
        self.redis = redis_async.from_url(connection_string, decode_responses=True)
        self.ttl = ttl

    async def get_user_location(self, user_id: str) -> Optional[dict]:
        """
        Obtiene la ubicación histórica del usuario
        
        Nota del desarrollador:
        La IA sugirió almacenar como string separado por comas.
        Lo cambié a JSON para ser más robusto y extensible.
        """
        data = await self.redis.get(f"user:{user_id}:location")
        if data is None:
            return None

        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    async def set_user_location(
        self, user_id: str, latitude: float, longitude: float, ttl: int = None
    ) -> None:
        """
        Almacena la ubicación del usuario en caché
        """
        if ttl is None:
            ttl = self.ttl

        location_data = json.dumps({"latitude": latitude, "longitude": longitude})
        await self.redis.setex(f"user:{user_id}:location", ttl, location_data)

    async def get_threshold_config(self) -> Optional[dict]:
        """
        Obtiene la configuración de umbrales desde caché (HU-008/009)
        """
        data = await self.redis.get("config:thresholds")
        if data is None:
            return None

        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    async def set_threshold_config(
        self, amount_threshold: float, location_radius_km: float
    ) -> None:
        """
        Almacena la configuración de umbrales en caché
        
        Nota del desarrollador:
        La IA sugirió no usar TTL para configuración. Agregué TTL
        de 1 año para evitar que Redis lo elimine por falta de uso,
        pero permitir limpieza eventual si el sistema se reconfigura.
        """
        config_data = json.dumps(
            {
                "amount_threshold": amount_threshold,
                "location_radius_km": location_radius_km,
            }
        )
        # TTL de 1 año (31536000 segundos)
        await self.redis.setex("config:thresholds", 31536000, config_data)
