"""
Amount Threshold Strategy - Detección de fraude por umbral de monto (HU-003)

Implementa el patrón Strategy para detectar transacciones que excedan un umbral

Cumplimiento SOLID:
- Single Responsibility: Solo evalúa umbral de monto
- Open/Closed: Implementa FraudStrategy sin modificarla
- Liskov Substitution: Puede sustituir a FraudStrategy
- Dependency Inversion: Depende de abstracción (FraudStrategy)
"""
from decimal import Decimal
from typing import Dict, Any, Optional
from .base import FraudStrategy
from ..models import Transaction, RiskLevel, Location


class AmountThresholdStrategy(FraudStrategy):
    """
    Estrategia que detecta fraude cuando el monto excede un umbral configurado
    
    HU-003: Marca como sospechosa cualquier transacción que exceda el umbral
    """

    def __init__(self, threshold: Decimal) -> None:
        """
        Inicializa la estrategia con un umbral de monto
        
        Args:
            threshold: Monto límite en Decimal (ej: 1500.00)
        
        Raises:
            ValueError: Si el umbral no es positivo
        """
        if threshold <= 0:
            raise ValueError("Threshold must be positive")
        self.threshold = threshold

    def evaluate(
        self, transaction: Transaction, historical_location: Optional[Location] = None
    ) -> Dict[str, Any]:
        """
        Evalúa si el monto de la transacción excede el umbral
        
        Args:
            transaction: Transacción a evaluar
            historical_location: No usado en esta estrategia
        
        Returns:
            Dict con risk_level, reasons y details
        
        Raises:
            ValueError: Si transaction es None
        """
        if transaction is None:
            raise ValueError("Transaction cannot be None")

        if transaction.amount > self.threshold:
            return {
                "risk_level": RiskLevel.HIGH_RISK,
                "reasons": ["amount_threshold_exceeded"],
                "details": f"amount: {transaction.amount} exceeds threshold: {self.threshold}",
            }

        return {"risk_level": RiskLevel.LOW_RISK, "reasons": [], "details": ""}
