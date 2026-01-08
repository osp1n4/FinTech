"""
Strategy Pattern - Interface base para estrategias de detección de fraude

Cumplimiento SOLID:
- Single Responsibility: Define contrato para evaluar transacciones
- Open/Closed: Abierto a extensión (nuevas estrategias), cerrado a modificación
- Liskov Substitution: Todas las estrategias son intercambiables
- Interface Segregation: Interface mínima y cohesiva
- Dependency Inversion: Los casos de uso dependen de esta abstracción
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models import Transaction, RiskLevel, Location


class FraudStrategy(ABC):
    """
    Interface base para estrategias de detección de fraude (Strategy Pattern)
    
    Todas las estrategias concretas deben implementar el método evaluate()
    """

    @abstractmethod
    def evaluate(
        self, transaction: Transaction, historical_location: Optional[Location] = None
    ) -> Dict[str, Any]:
        """
        Evalúa una transacción y retorna el resultado del análisis
        
        Args:
            transaction: Transacción a evaluar
            historical_location: Ubicación histórica del usuario (opcional)
        
        Returns:
            Dict con:
                - risk_level: RiskLevel (LOW_RISK, MEDIUM_RISK, HIGH_RISK)
                - reasons: List[str] con razones de la evaluación
                - details: str con información adicional
        """
        pass
