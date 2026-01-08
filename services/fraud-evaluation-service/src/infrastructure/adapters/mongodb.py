"""
MongoDB Adapter - Implementación concreta de TransactionRepository

Cumplimiento SOLID:
- Dependency Inversion: Implementa la interface TransactionRepository
- Single Responsibility: Solo maneja persistencia en MongoDB
"""
from typing import List, Optional
from pymongo import MongoClient
from datetime import datetime
from decimal import Decimal
from ...application.interfaces import TransactionRepository
from ...domain.models import FraudEvaluation, RiskLevel, Location


class MongoDBAdapter(TransactionRepository):
    """Adaptador de MongoDB que implementa TransactionRepository"""

    def __init__(self, connection_string: str, database_name: str) -> None:
        """
        Inicializa el adaptador de MongoDB
        
        Args:
            connection_string: URL de conexión a MongoDB
            database_name: Nombre de la base de datos
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db["fraud_evaluations"]

    async def save_evaluation(self, evaluation: FraudEvaluation) -> None:
        """Persiste una evaluación de fraude"""
        document = self._evaluation_to_dict(evaluation)
        self.collection.insert_one(document)

    async def get_all_evaluations(self) -> List[FraudEvaluation]:
        """Obtiene todas las evaluaciones históricas"""
        cursor = self.collection.find().sort("timestamp", -1)
        return [self._dict_to_evaluation(doc) for doc in cursor]

    async def get_evaluation_by_id(
        self, transaction_id: str
    ) -> Optional[FraudEvaluation]:
        """Obtiene una evaluación específica por ID"""
        document = self.collection.find_one({"transaction_id": transaction_id})
        if document is None:
            return None
        return self._dict_to_evaluation(document)

    async def update_evaluation(self, evaluation: FraudEvaluation) -> None:
        """Actualiza una evaluación existente"""
        document = self._evaluation_to_dict(evaluation)
        result = self.collection.update_one(
            {"transaction_id": evaluation.transaction_id},
            {"$set": document}
        )
        if result.matched_count == 0:
            raise ValueError(f"Evaluation {evaluation.transaction_id} not found")

    def _evaluation_to_dict(self, evaluation: FraudEvaluation) -> dict:
        """Convierte FraudEvaluation a dict para MongoDB"""
        return {
            "transaction_id": evaluation.transaction_id,
            "user_id": evaluation.user_id,
            "risk_level": evaluation.risk_level.name,
            "reasons": evaluation.reasons,
            "timestamp": evaluation.timestamp,
            "amount": float(evaluation.amount) if evaluation.amount else None,
            "location": {
                "latitude": evaluation.location.latitude,
                "longitude": evaluation.location.longitude,
            } if evaluation.location else None,
            "status": evaluation.status,
            "reviewed_by": evaluation.reviewed_by,
            "reviewed_at": evaluation.reviewed_at,
            "user_authenticated": evaluation.user_authenticated,
            "user_auth_timestamp": evaluation.user_auth_timestamp,
        }

    def _dict_to_evaluation(self, doc: dict) -> FraudEvaluation:
        """Convierte dict de MongoDB a FraudEvaluation"""
        location = None
        if doc.get("location"):
            location = Location(
                latitude=doc["location"]["latitude"],
                longitude=doc["location"]["longitude"],
            )

        return FraudEvaluation(
            transaction_id=doc["transaction_id"],
            user_id=doc["user_id"],
            risk_level=RiskLevel[doc["risk_level"]],
            reasons=doc["reasons"],
            timestamp=doc["timestamp"],
            amount=Decimal(str(doc["amount"])) if doc.get("amount") else None,
            location=location,
            status=doc["status"],
            reviewed_by=doc.get("reviewed_by"),
            reviewed_at=doc.get("reviewed_at"),
            user_authenticated=doc.get("user_authenticated"),
            user_auth_timestamp=doc.get("user_auth_timestamp"),
        )
