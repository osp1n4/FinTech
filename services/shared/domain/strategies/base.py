"""
Strategy Pattern - Interface base para estrategias de detección de fraude

Cumplimiento SOLID:
- Single Responsibility: Define contrato para evaluar transacciones
- Open/Closed: Abierto a extensión (nuevas estrategias), cerrado a modificación
- Liskov Substitution: Todas las estrategias son intercambiables
- Interface Segregation: Interface mínima y cohesiva
- Dependency Inversion: Los casos de uso dependen de esta abstracción

Nota del desarrollador (María Gutiérrez):
La IA sugirió un método evaluate() que retornaba bool. Lo refactoricé para retornar
un diccionario estructurado con risk_level, reasons y details. Esto cumple mejor con
el principio "Tell, don't ask" y proporciona información rica para auditoría.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from services.shared.domain.models import Transaction, RiskLevel, Location


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
            historical_location: Ubicación histórica del usuario (opcional, solo para LocationStrategy)
        
        Returns:
            Dict con:
                - risk_level: RiskLevel (LOW_RISK, MEDIUM_RISK, HIGH_RISK)
                - reasons: List[str] con razones de la evaluación
                - details: str con información adicional
        
        Nota del desarrollador:
        El parámetro historical_location es opcional porque solo LocationStrategy lo usa.
        La IA propuso dos métodos separados, pero lo unifiqué para cumplir con
        "Interface Segregation" manteniendo la interface mínima.
        """
        pass
