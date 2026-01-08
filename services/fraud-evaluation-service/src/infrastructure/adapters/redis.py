"""
Redis Adapter - Implementación concreta de CacheService

Cumplimiento SOLID:
- Dependency Inversion: Implementa la interface CacheService
- Single Responsibility: Solo maneja caché con Redis
"""
from typing import Optional
import redis.asyncio as redis_async
import json


class RedisAdapter:
    """Adaptador de Redis que implementa CacheService"""

    def __init__(self, redis_url: str, ttl: int = 86400) -> None:
        """
        Inicializa el adaptador de Redis
        
        Args:
            redis_url: URL de conexión a Redis
            ttl: Tiempo de vida por defecto en segundos
        """
        self.redis_url = redis_url
        self.default_ttl = ttl
        self.client: Optional[redis_async.Redis] = None

    async def connect(self) -> None:
        """Establece conexión con Redis"""
        self.client = await redis_async.from_url(self.redis_url, decode_responses=True)

    async def disconnect(self) -> None:
        """Cierra conexión con Redis"""
        if self.client:
            await self.client.close()

    async def get_user_location(self, user_id: str) -> Optional[dict]:
        """Obtiene la ubicación histórica de un usuario desde caché"""
        if not self.client:
            await self.connect()
        
        key = f"location:{user_id}"
        data = await self.client.get(key)
        
        if data is None:
            return None
        
        return json.loads(data)

    async def set_user_location(
        self, user_id: str, latitude: float, longitude: float, ttl: int = None
    ) -> None:
        """Almacena la ubicación de un usuario en caché"""
        if not self.client:
            await self.connect()
        
        key = f"location:{user_id}"
        value = json.dumps({"latitude": latitude, "longitude": longitude})
        ttl = ttl or self.default_ttl
        
        await self.client.setex(key, ttl, value)

    async def get_threshold_config(self) -> Optional[dict]:
        """Obtiene la configuración de umbrales desde caché"""
        if not self.client:
            await self.connect()
        
        key = "config:thresholds"
        data = await self.client.get(key)
        
        if data is None:
            return None
        
        return json.loads(data)

    async def set_threshold_config(
        self, amount_threshold: float, location_radius_km: float
    ) -> None:
        """Almacena la configuración de umbrales en caché"""
        if not self.client:
            await self.connect()
        
        key = "config:thresholds"
        value = json.dumps({
            "amount_threshold": amount_threshold,
            "location_radius_km": location_radius_km,
        })
        
        await self.client.set(key, value)
