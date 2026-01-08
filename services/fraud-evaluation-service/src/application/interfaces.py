"""
Application Layer - Interfaces (Puertos)
Define contratos que la Infrastructure debe implementar

Cumplimiento SOLID:
- Interface Segregation: Cada interface es específica y cohesiva
- Dependency Inversion: Application depende de abstracciones, no de implementaciones
- Single Responsibility: Cada interface tiene un propósito único
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.models import FraudEvaluation


class TransactionRepository(ABC):
    """
    Puerto para persistencia de evaluaciones de fraude
    
    Permite al Application Layer guardar y consultar evaluaciones sin
    conocer los detalles de implementación (MongoDB, PostgreSQL, etc.)
    """

    @abstractmethod
    async def save_evaluation(self, evaluation: FraudEvaluation) -> None:
        """
        Persiste una evaluación de fraude
        
        Args:
            evaluation: Evaluación a guardar
        
        Raises:
            RepositoryError: Si falla la persistencia
        """
        pass

    @abstractmethod
    async def get_all_evaluations(self) -> List[FraudEvaluation]:
        """
        Obtiene todas las evaluaciones históricas
        
        Returns:
            Lista de evaluaciones ordenadas por timestamp descendente
        """
        pass

    @abstractmethod
    async def get_evaluation_by_id(
        self, transaction_id: str
    ) -> Optional[FraudEvaluation]:
        """
        Obtiene una evaluación específica por ID de transacción
        
        Args:
            transaction_id: ID de la transacción
        
        Returns:
            FraudEvaluation si existe, None si no se encuentra
        """
        pass

    @abstractmethod
    async def update_evaluation(self, evaluation: FraudEvaluation) -> None:
        """
        Actualiza una evaluación existente (para revisión manual)
        
        Args:
            evaluation: Evaluación actualizada
        
        Raises:
            RepositoryError: Si falla la actualización
            NotFoundError: Si la evaluación no existe
        """
        pass


class MessagePublisher(ABC):
    """
    Puerto para publicación de mensajes en cola (RabbitMQ, Kafka, etc.)
    
    Permite desacoplar el Application Layer del sistema de mensajería concreto
    """

    @abstractmethod
    async def publish_transaction_for_processing(
        self, transaction_data: dict
    ) -> None:
        """
        Publica una transacción en la cola para procesamiento asíncrono
        
        Args:
            transaction_data: Datos de la transacción en formato dict
        
        Raises:
            PublisherError: Si falla la publicación
        """
        pass

    @abstractmethod
    async def publish_for_manual_review(self, evaluation_data: dict) -> None:
        """
        Publica una evaluación en la cola de revisión manual
        
        Args:
            evaluation_data: Datos de la evaluación en formato dict
        
        Raises:
            PublisherError: Si falla la publicación
        """
        pass


class CacheService(ABC):
    """
    Puerto para servicio de caché (Redis, Memcached, etc.)
    
    Permite almacenar y recuperar datos temporales sin conocer la implementación
    """

    @abstractmethod
    async def get_user_location(self, user_id: str) -> Optional[dict]:
        """
        Obtiene la ubicación histórica de un usuario desde caché
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Dict con 'latitude' y 'longitude' si existe, None si no hay datos
        """
        pass

    @abstractmethod
    async def set_user_location(
        self, user_id: str, latitude: float, longitude: float, ttl: int = 86400
    ) -> None:
        """
        Almacena la ubicación de un usuario en caché
        
        Args:
            user_id: ID del usuario
            latitude: Latitud
            longitude: Longitud
            ttl: Tiempo de vida en segundos (por defecto 24 horas)
        
        Raises:
            CacheError: Si falla el almacenamiento
        """
        pass

    @abstractmethod
    async def get_threshold_config(self) -> Optional[dict]:
        """
        Obtiene la configuración de umbrales desde caché
        
        Returns:
            Dict con 'amount_threshold' y 'location_radius_km' si existe
        """
        pass

    @abstractmethod
    async def set_threshold_config(
        self, amount_threshold: float, location_radius_km: float
    ) -> None:
        """
        Almacena la configuración de umbrales en caché
        
        Args:
            amount_threshold: Umbral de monto
            location_radius_km: Radio de ubicación en km
        
        Raises:
            CacheError: Si falla el almacenamiento
        """
        pass
