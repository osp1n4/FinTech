"""
Application Layer - Casos de Uso
Orquesta la lógica de negocio coordinando Domain y Infrastructure

Cumplimiento SOLID:
- Single Responsibility: Cada caso de uso tiene una responsabilidad única
- Open/Closed: Extensible mediante nuevas estrategias sin modificar código
- Dependency Inversion: Depende de interfaces (puertos), no de implementaciones
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
from ..domain.models import Transaction, FraudEvaluation, Location, RiskLevel
from ..domain.strategies.base import FraudStrategy
from .interfaces import TransactionRepository, MessagePublisher, CacheService


class EvaluateTransactionUseCase:
    """
    Caso de uso: Evaluar una transacción usando estrategias de fraude
    
    HU-001: Recibe transacción y ejecuta evaluación asíncrona
    HU-003 y HU-005: Aplica reglas de negocio (monto y ubicación)
    """

    def __init__(
        self,
        repository: TransactionRepository,
        publisher: MessagePublisher,
        cache: CacheService,
        strategies: List[FraudStrategy],
    ) -> None:
        """
        Inicializa el caso de uso con sus dependencias
        
        Args:
            repository: Puerto para persistencia
            publisher: Puerto para mensajería
            cache: Puerto para caché
            strategies: Lista de estrategias de detección
        """
        self.repository = repository
        self.publisher = publisher
        self.cache = cache
        self.strategies = strategies

    async def execute(self, transaction_data: dict) -> Dict[str, Any]:
        """
        Ejecuta la evaluación de una transacción
        
        Args:
            transaction_data: Dict con datos de la transacción
        
        Returns:
            Dict con resultado de la evaluación
        
        Raises:
            ValueError: Si los datos son inválidos
            KeyError: Si faltan campos requeridos
        """
        # 1. Convertir datos a entidad Transaction
        transaction = self._build_transaction_from_data(transaction_data)

        # 2. Obtener ubicación histórica del usuario (si existe)
        historical_location = await self._get_historical_location(transaction.user_id)

        # 3. Ejecutar todas las estrategias y combinar resultados
        all_reasons = []
        rules_violated = 0

        for strategy in self.strategies:
            result = strategy.evaluate(transaction, historical_location)
            
            if result["reasons"]:
                rules_violated += 1
                all_reasons.extend(result["reasons"])
        
        # Determinar riesgo basado en reglas incumplidas
        if rules_violated == 0:
            risk_level = RiskLevel.LOW_RISK
        elif rules_violated == 1:
            risk_level = RiskLevel.MEDIUM_RISK
        else:
            risk_level = RiskLevel.HIGH_RISK

        # 4. Crear evaluación
        evaluation = FraudEvaluation(
            transaction_id=transaction.id,
            user_id=transaction.user_id,
            risk_level=risk_level,
            reasons=all_reasons,
            timestamp=datetime.now(),
            amount=transaction.amount,
            location=transaction.location,
        )

        # 5. Persistir evaluación
        await self.repository.save_evaluation(evaluation)

        # 6. Actualizar ubicación en caché
        await self.cache.set_user_location(
            user_id=transaction.user_id,
            latitude=transaction.location.latitude,
            longitude=transaction.location.longitude,
        )

        # 7. Si es riesgo alto o medio, enviar a revisión manual
        if risk_level in (RiskLevel.HIGH_RISK, RiskLevel.MEDIUM_RISK):
            await self.publisher.publish_for_manual_review(
                {
                    "transaction_id": transaction.id,
                    "risk_level": risk_level.name,
                    "reasons": all_reasons,
                    "amount": float(transaction.amount),
                    "user_id": transaction.user_id,
                }
            )

        # 8. Retornar resultado
        return {
            "transaction_id": transaction.id,
            "risk_level": risk_level.name,
            "reasons": all_reasons,
            "status": evaluation.status,
        }

    def _build_transaction_from_data(self, data: dict) -> Transaction:
        """Construye una entidad Transaction desde datos dict"""
        try:
            location_data = data["location"]
            location = Location(
                latitude=float(location_data["latitude"]),
                longitude=float(location_data["longitude"]),
            )

            timestamp_str = data.get("timestamp")
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            else:
                timestamp = datetime.now()

            return Transaction(
                id=data["id"],
                amount=Decimal(str(data["amount"])),
                user_id=data["user_id"],
                location=location,
                timestamp=timestamp,
            )
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid data format: {e}")

    async def _get_historical_location(self, user_id: str) -> Optional[Location]:
        """Obtiene la ubicación histórica del usuario desde caché"""
        location_data = await self.cache.get_user_location(user_id)
        if location_data is None:
            return None

        try:
            return Location(
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
            )
        except (KeyError, ValueError):
            return None


class ReviewTransactionUseCase:
    """
    Caso de uso: Revisar transacción manualmente (Human in the Loop)
    
    HU-010: Permite al analista aprobar o rechazar una transacción
    """

    def __init__(self, repository: TransactionRepository) -> None:
        """
        Inicializa el caso de uso con su dependencia
        
        Args:
            repository: Puerto para persistencia
        """
        self.repository = repository

    async def execute(
        self, transaction_id: str, decision: str, analyst_id: str
    ) -> None:
        """
        Aplica una decisión manual a una transacción
        
        Args:
            transaction_id: ID de la transacción
            decision: 'APPROVED' o 'REJECTED'
            analyst_id: ID del analista
        
        Raises:
            ValueError: Si la transacción no existe o la decisión es inválida
        """
        # 1. Obtener evaluación existente
        evaluation = await self.repository.get_evaluation_by_id(transaction_id)

        if evaluation is None:
            raise ValueError(f"Transaction {transaction_id} not found")

        # 2. Aplicar decisión manual
        evaluation.apply_manual_decision(decision, analyst_id)

        # 3. Persistir actualización
        await self.repository.update_evaluation(evaluation)
