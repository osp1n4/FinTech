"""
Infrastructure - Adaptadores para persistencia, caché y mensajería

Exporta todos los adaptadores para facilitar las importaciones.
Refactorizado por: María Gutiérrez
Fecha: Enero 2026

Cumplimiento SOLID:
- Cada adaptador en su propio archivo (SRP a nivel módulo)
- Interface Segregation: Cada adaptador implementa solo una interfaz
- Dependency Inversion: Todos implementan interfaces de Application Layer
"""
from .mongodb_adapter import MongoDBAdapter
from .redis_adapter import RedisAdapter
from .rabbitmq_adapter import RabbitMQAdapter

__all__ = ["MongoDBAdapter", "RedisAdapter", "RabbitMQAdapter"]
