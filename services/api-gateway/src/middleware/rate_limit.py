"""
Rate Limiting Middleware - Control de tasa de peticiones

Cumple Single Responsibility: Solo maneja rate limiting
"""
from fastapi import HTTPException, Request, status
from typing import Dict
from datetime import datetime, timedelta
import asyncio


class RateLimiter:
    """
    Rate limiter simple basado en memoria
    
    En producción se debería usar Redis para almacenamiento distribuido
    """
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Inicializa el rate limiter
        
        Args:
            requests_per_minute: Número máximo de peticiones por minuto
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}  # {client_id: [timestamps]}
    
    def _clean_old_requests(self, client_id: str) -> None:
        """Limpia peticiones antiguas (más de 1 minuto)"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        if client_id in self.requests:
            self.requests[client_id] = [
                timestamp for timestamp in self.requests[client_id]
                if timestamp > cutoff
            ]
    
    def check_rate_limit(self, client_id: str) -> None:
        """
        Verifica si el cliente ha excedido el límite de peticiones
        
        Args:
            client_id: Identificador del cliente (IP, user_id, etc.)
        
        Raises:
            HTTPException: Si se excede el límite
        """
        # Limpiar peticiones antiguas
        self._clean_old_requests(client_id)
        
        # Verificar límite
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        if len(self.requests[client_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
            )
        
        # Registrar nueva petición
        self.requests[client_id].append(datetime.now())


# Instancia global del rate limiter
rate_limiter = RateLimiter(requests_per_minute=60)


async def check_rate_limit(request: Request) -> None:
    """
    Middleware function para verificar rate limit
    
    Args:
        request: Request de FastAPI
    
    Raises:
        HTTPException: Si se excede el límite
    """
    # Usar IP del cliente como identificador
    client_id = request.client.host
    
    # Verificar límite
    rate_limiter.check_rate_limit(client_id)
