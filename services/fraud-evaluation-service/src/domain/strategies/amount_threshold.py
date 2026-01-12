"""
Amount Threshold Strategy - Detección de fraude por umbral de monto (HU-003)

Implementa el patrón Strategy para detectar transacciones que excedan un umbral

Cumplimiento SOLID:
- Single Responsibility: Solo evalúa umbral de monto
- Open/Closed: Implementa FraudStrategy sin modificarla
- Liskov Substitution: Puede sustituir a FraudStrategy
- Dependency Inversion: Depende de abstracción (FraudStrategy)

Nota del desarrollador (María Gutiérrez):
La IA sugirió comparación con >= para el umbral. Lo cambié a > (estrictamente mayor)
porque el requerimiento de negocio dice "que exceda $1,500", no "igual o mayor".
Esto previene falsos positivos en transacciones exactamente en el límite.
"""
from decimal import Decimal
from typing import Dict, Any, Optional
from src.domain.strategies.base import FraudStrategy
from src.domain.models import Transaction, RiskLevel, Location


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
        
        Nota del desarrollador:
        Uso Decimal en lugar de float para evitar errores de precisión
        en operaciones financieras. La IA propuso float, lo refactoricé.
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
            historical_location: No usado en esta estrategia (solo para cumplir interface)
        
        Returns:
            Dict con risk_level, reasons y details
        
        Raises:
            ValueError: Si transaction es None
        """
        if transaction is None:
            raise ValueError("Transaction cannot be None")

        # Nota del desarrollador:
        # La IA sugirió if/else anidado. Lo simplifiqué usando retornos tempranos
        # (guard clauses) para mejorar legibilidad y cumplir con "Flat is better than nested".
        # Usar valor absoluto para validar transferencias (negativas) y depósitos (positivos)
        amount_abs = abs(transaction.amount)
        
        if amount_abs > self.threshold:
            return {
                "risk_level": RiskLevel.HIGH_RISK,
                "reasons": ["amount_threshold_exceeded"],
                "details": f"amount: {amount_abs} exceeds threshold: {self.threshold}",
            }

        return {"risk_level": RiskLevel.LOW_RISK, "reasons": [], "details": ""}

