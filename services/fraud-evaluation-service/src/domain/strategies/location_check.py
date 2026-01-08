"""
Location Check Strategy - Detección de fraude por ubicación inusual (HU-005)

Implementa el patrón Strategy para detectar transacciones fuera del radio habitual

Cumplimiento SOLID:
- Single Responsibility: Solo evalúa distancia geográfica
- Open/Closed: Implementa FraudStrategy sin modificarla
- Liskov Substitution: Puede sustituir a FraudStrategy
- Dependency Inversion: Depende de abstracción (FraudStrategy)
"""
from math import radians, cos, sin, asin, sqrt
from typing import Dict, Any, Optional
from .base import FraudStrategy
from ..models import Transaction, RiskLevel, Location


class LocationStrategy(FraudStrategy):
    """
    Estrategia que detecta fraude cuando la ubicación está fuera del radio habitual
    
    HU-005: Previene fraudes por takeover geográfico (fuera del radio de 100 km)
    """

    def __init__(self, radius_km: float) -> None:
        """
        Inicializa la estrategia con un radio máximo permitido
        
        Args:
            radius_km: Radio máximo en kilómetros (ej: 100)
        
        Raises:
            ValueError: Si el radio no es positivo
        """
        if radius_km <= 0:
            raise ValueError("Radius must be positive")
        self.radius_km = radius_km

    def evaluate(
        self, transaction: Transaction, historical_location: Optional[Location] = None
    ) -> Dict[str, Any]:
        """
        Evalúa si la ubicación de la transacción está fuera del radio habitual
        
        Args:
            transaction: Transacción a evaluar
            historical_location: Ubicación histórica del usuario
        
        Returns:
            Dict con risk_level, reasons y details
        
        Raises:
            ValueError: Si transaction es None
        """
        if transaction is None:
            raise ValueError("Transaction cannot be None")

        # Usuario sin historial de ubicación (primera transacción)
        if historical_location is None:
            return {
                "risk_level": RiskLevel.LOW_RISK,
                "reasons": ["no_historical_location"],
                "details": "First transaction for user, no historical location",
            }

        # Calcular distancia usando fórmula de Haversine
        distance_km = self._calculate_distance(
            historical_location, transaction.location
        )

        if distance_km > self.radius_km:
            return {
                "risk_level": RiskLevel.HIGH_RISK,
                "reasons": ["unusual_location"],
                "details": (
                    f"distance: {distance_km:.2f} km exceeds radius: {self.radius_km} km. "
                    f"Previous: ({historical_location.latitude}, {historical_location.longitude}), "
                    f"Current: ({transaction.location.latitude}, {transaction.location.longitude})"
                ),
            }

        return {"risk_level": RiskLevel.LOW_RISK, "reasons": [], "details": ""}

    def _calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """
        Calcula la distancia entre dos ubicaciones usando la fórmula de Haversine
        
        Args:
            loc1: Primera ubicación
            loc2: Segunda ubicación
        
        Returns:
            Distancia en kilómetros
        """
        # Radio de la Tierra en kilómetros
        earth_radius_km = 6371.0

        # Convertir grados a radianes
        lat1 = radians(loc1.latitude)
        lon1 = radians(loc1.longitude)
        lat2 = radians(loc2.latitude)
        lon2 = radians(loc2.longitude)

        # Diferencias
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Fórmula de Haversine
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        # Distancia en kilómetros
        distance = earth_radius_km * c

        return distance
