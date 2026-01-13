"""
Módulo de estrategias de detección de fraude.
Implementa el patrón Strategy para diferentes reglas de detección.
"""

from .base import FraudStrategy
from .amount_threshold import AmountThresholdStrategy
from .location_check import LocationStrategy
from .device_validation import DeviceValidationStrategy
from .rapid_transaction import RapidTransactionStrategy
from .unusual_time import UnusualTimeStrategy

__all__ = [
    'FraudStrategy',
    'AmountThresholdStrategy',
    'LocationStrategy',
    'DeviceValidationStrategy',
    'RapidTransactionStrategy',
    'UnusualTimeStrategy',
]

