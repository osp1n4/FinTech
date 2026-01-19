"""
MongoDB Adapter - Implementación de TransactionRepository

Cumplimiento SOLID:
- Single Responsibility: Solo maneja persistencia en MongoDB
- Dependency Inversion: Implementa interface TransactionRepository
- Open/Closed: Extensible sin modificar código existente

Nota del desarrollador (María Gutiérrez):
Extraído de adapters.py para mejor organización y escalabilidad.
La IA sugirió usar Motor (driver asíncrono). Lo cambié a pymongo
simple para mantener el MVP minimalista. Se puede refactorizar
a Motor después si es necesario (YAGNI principle).
"""
from typing import List, Optional
from pymongo import MongoClient

from src.application.interfaces import TransactionRepository
from src.domain.models import FraudEvaluation, RiskLevel


class MongoDBAdapter(TransactionRepository):
    """
    Adaptador de MongoDB que implementa TransactionRepository
    
    Cumple Dependency Inversion: Application depende de la interface,
    no de esta implementación concreta
    """

    def __init__(self, connection_string: str, database_name: str) -> None:
        """
        Inicializa el adaptador de MongoDB
        
        Args:
            connection_string: URL de conexión a MongoDB
            database_name: Nombre de la base de datos
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.evaluations = self.db.evaluations

        # Crear índices para mejorar performance
        self.evaluations.create_index("transaction_id", unique=True)
        self.evaluations.create_index([("timestamp", -1)])

    async def save_evaluation(self, evaluation: FraudEvaluation) -> None:
        """
        Guarda una evaluación en MongoDB
        
        Nota del desarrollador:
        La IA sugirió guardar la entidad directamente. Agregué conversión
        explícita a dict para controlar la serialización y evitar problemas
        con tipos de Python no soportados por MongoDB.
        """
        document = {
            "transaction_id": evaluation.transaction_id,
            "risk_level": evaluation.risk_level.value,
            "reasons": evaluation.reasons,
            "timestamp": evaluation.timestamp,
            "status": evaluation.status,
            "reviewed_by": evaluation.reviewed_by,
            "reviewed_at": evaluation.reviewed_at,
        }
        self.evaluations.insert_one(document)

    async def get_all_evaluations(self) -> List[FraudEvaluation]:
        """
        Obtiene todas las evaluaciones ordenadas por timestamp descendente
        
        Nota del desarrollador:
        La IA sugirió retornar los documentos directamente. Agregué conversión
        a entidades FraudEvaluation para mantener el Domain Model en toda
        la aplicación y evitar "Primitive Obsession".
        """
        documents = self.evaluations.find().sort("timestamp", -1)
        return [self._document_to_evaluation(doc) for doc in documents]

    async def get_evaluation_by_id(
        self, transaction_id: str
    ) -> Optional[FraudEvaluation]:
        """
        Obtiene una evaluación específica por ID
        """
        document = self.evaluations.find_one({"transaction_id": transaction_id})
        if document is None:
            return None
        return self._document_to_evaluation(document)

    async def update_evaluation(self, evaluation: FraudEvaluation) -> None:
        """
        Actualiza una evaluación existente
        
        Raises:
            ValueError: Si la evaluación no existe
        """
        result = self.evaluations.update_one(
            {"transaction_id": evaluation.transaction_id},
            {
                "$set": {
                    "status": evaluation.status,
                    "reviewed_by": evaluation.reviewed_by,
                    "reviewed_at": evaluation.reviewed_at,
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError(f"Transaction {evaluation.transaction_id} not found")

    def _document_to_evaluation(self, document: dict) -> FraudEvaluation:
        """
        Convierte un documento de MongoDB a entidad FraudEvaluation
        
        Nota del desarrollador:
        La IA olvidó manejar el enum RiskLevel. Agregué conversión explícita
        para evitar errores de tipos.
        """
        return FraudEvaluation(
            transaction_id=document["transaction_id"],
            risk_level=RiskLevel[document["risk_level"]],  # Usar RiskLevel[name] en lugar de RiskLevel(value)
            reasons=document["reasons"],
            timestamp=document["timestamp"],
            status=document.get("status", "PENDING_REVIEW"),
            reviewed_by=document.get("reviewed_by"),
            reviewed_at=document.get("reviewed_at"),
        )
