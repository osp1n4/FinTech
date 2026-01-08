"""
Device Validation Strategy - Detección de fraude por dispositivo desconocido

Implementa el patrón Strategy para detectar transacciones desde dispositivos no registrados

Cumplimiento SOLID:
- Single Responsibility: Solo evalúa dispositivo
- Open/Closed: Implementa FraudStrategy sin modificarla
- Liskov Substitution: Puede sustituir a FraudStrategy
- Dependency Inversion: Depende de abstracción (FraudStrategy)
"""
from typing import Dict, Any, Optional, Set
from .base import FraudStrategy
from ..models import Transaction, RiskLevel, Location


class DeviceValidationStrategy(FraudStrategy):
    """
    Estrategia que detecta fraude cuando el dispositivo no está registrado
    
    Requiere que el device_id de la transacción esté en la lista de dispositivos conocidos
    """

    def __init__(self, known_devices: Set[str]) -> None:
        """
        Inicializa la estrategia con dispositivos conocidos
        
        Args:
            known_devices: Set de device IDs registrados para el usuario
        
        Raises:
            ValueError: Si known_devices es None
        """
        if known_devices is None:
            raise ValueError("Known devices set cannot be None")
        self.known_devices = known_devices

    def evaluate(
        self, transaction: Transaction, historical_location: Optional[Location] = None
    ) -> Dict[str, Any]:
        """
        Evalúa si el dispositivo está registrado
        
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

        # Obtener device_id de la transacción (si existe como atributo)
        device_id = getattr(transaction, 'device_id', None)
        
        # Si no hay device_id, consideramos riesgo medio
        if device_id is None:
            return {
                "risk_level": RiskLevel.MEDIUM_RISK,
                "reasons": ["no_device_id"],
                "details": "Transaction has no device ID",
            }

        # Si el device_id no está en la lista de conocidos, es alto riesgo
        if device_id not in self.known_devices:
            return {
                "risk_level": RiskLevel.HIGH_RISK,
                "reasons": ["unknown_device"],
                "details": f"Device ID {device_id} is not registered",
            }

        return {"risk_level": RiskLevel.LOW_RISK, "reasons": [], "details": ""}
