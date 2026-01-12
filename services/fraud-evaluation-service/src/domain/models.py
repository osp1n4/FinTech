"""
Domain Models - Entidades y Value Objects
Implementación siguiendo TDD y principios SOLID

Cumplimiento SOLID:
- Single Responsibility: Cada clase tiene una única razón para cambiar
- Open/Closed: Extensible mediante herencia sin modificación
- Liskov Substitution: Las entidades pueden ser sustituidas por sus subtipos
- Interface Segregation: N/A en este módulo (no hay interfaces)
- Dependency Inversion: No depende de implementaciones concretas

Nota del desarrollador (María Gutiérrez):
La IA sugirió usar un dict para Location. Lo refactoricé a un Value Object inmutable
para cumplir con DDD (Domain-Driven Design) y garantizar validación en construcción.
Esto previene estados inválidos y cumple el principio "Make Invalid States Unrepresentable".
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class RiskLevel(Enum):
    """
    Enum que representa los niveles de riesgo de fraude
    
    Inmutable por diseño (Enum) - cumple principio de Value Object
    Valores numéricos permiten comparación por gravedad (LOW < MEDIUM < HIGH)
    """

    LOW_RISK = 1
    MEDIUM_RISK = 2
    HIGH_RISK = 3
    
    def __str__(self):
        """Retorna el nombre del enum para serialización"""
        return self.name


@dataclass(frozen=True)
class Location:
    """
    Value Object que representa una ubicación geográfica
    
    Inmutable (frozen=True) - garantiza thread-safety y comportamiento de Value Object
    Validación en construcción - previene estados inválidos (principio: fail fast)
    
    Nota del desarrollador:
    La IA sugirió validar en setters. Lo cambié a validación en __post_init__
    para cumplir con inmutabilidad y evitar ventanas de estado inconsistente.
    """

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Valida las coordenadas al momento de construcción"""
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")


@dataclass
class Transaction:
    """
    Entidad que representa una transacción financiera
    
    Es una entidad (no Value Object) porque tiene identidad única (id)
    y su estado puede cambiar en el tiempo (aunque los campos son inmutables aquí)
    
    Cumple Single Responsibility: Solo representa datos de transacción
    """

    id: str
    amount: Decimal
    user_id: str
    location: Location
    timestamp: datetime
    device_id: Optional[str] = None
    transaction_type: Optional[str] = None  # 'transfer', 'payment', 'recharge', 'deposit'
    description: Optional[str] = None  # Descripción o destinatario

    def __post_init__(self) -> None:
        """
        Validación de reglas de negocio al momento de construcción
        
        Nota del desarrollador:
        La IA propuso validaciones dispersas. Las centralicé en __post_init__
        para cumplir con "validación en un solo lugar" y evitar duplicación.
        """
        if not self.id or not self.id.strip():
            raise ValueError("Transaction ID cannot be empty")

        # Permitir montos negativos (transferencias/pagos) y positivos (depósitos)
        if self.amount == 0:
            raise ValueError("Amount cannot be zero")

        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")

        if self.location is None:
            raise ValueError("Location cannot be None")


@dataclass
class FraudEvaluation:
    """
    Entidad que representa el resultado de una evaluación de fraude
    
    Tiene identidad (transaction_id) y su estado cambia (status, reviewed_by)
    
    Cumple Single Responsibility: Solo maneja el resultado de evaluación
    Cumple Open/Closed: Puede extenderse con nuevos estados sin modificación
    
    Nota del desarrollador:
    La IA sugirió un método update_status() genérico. Lo refactoricé a
    apply_manual_decision() para expresar mejor la intención de negocio
    y cumplir con "Ubiquitous Language" de DDD.
    """

    transaction_id: str
    user_id: str
    risk_level: RiskLevel
    reasons: List[str]
    timestamp: datetime
    amount: Optional[Decimal] = None
    location: Optional[Location] = None
    status: str = ""  # Se calcula en __post_init__
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    user_authenticated: Optional[bool] = None  # Si el usuario confirmó la transacción
    user_auth_timestamp: Optional[datetime] = None  # Cuándo el usuario autenticó
    transaction_type: Optional[str] = None  # Tipo de transacción
    description: Optional[str] = None  # Descripción o destinatario

    def __post_init__(self) -> None:
        """
        Inicializa el estado basado en el nivel de riesgo
        
        Regla de negocio: LOW_RISK se aprueba automáticamente,
        MEDIUM y HIGH requieren revisión manual
        """
        if not self.transaction_id or not self.transaction_id.strip():
            raise ValueError("Transaction ID cannot be empty")
        
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")

        # Determinar estado inicial basado en nivel de riesgo
        # Nueva lógica: LOW_RISK = APPROVED, MEDIUM_RISK = PENDING_REVIEW, HIGH_RISK = REJECTED
        if not self.status:  # Solo si no fue establecido manualmente
            if self.risk_level == RiskLevel.LOW_RISK:
                self.status = "APPROVED"
            elif self.risk_level == RiskLevel.MEDIUM_RISK:
                self.status = "PENDING_REVIEW"
            else:  # HIGH_RISK
                self.status = "REJECTED"

    def apply_manual_decision(self, decision: str, analyst_id: str) -> None:
        """
        Aplica una decisión manual de un analista
        
        Args:
            decision: 'APPROVED' o 'REJECTED'
            analyst_id: ID del analista que toma la decisión
        
        Raises:
            ValueError: Si la decisión o analyst_id son inválidos
        
        Nota del desarrollador:
        La IA sugirió aceptar cualquier string. Agregué validación estricta
        para cumplir con "Parse, don't validate" y prevenir bugs silenciosos.
        """
        if decision not in ("APPROVED", "REJECTED"):
            raise ValueError("Invalid decision. Must be 'APPROVED' or 'REJECTED'")

        if not analyst_id or not analyst_id.strip():
            raise ValueError("Analyst ID cannot be empty")

        self.status = decision
        self.reviewed_by = analyst_id
        self.reviewed_at = datetime.now()

    def authenticate_by_user(self, confirmed: bool) -> None:
        """
        El usuario confirma o rechaza la transacción (autenticación adicional)
        
        Args:
            confirmed: True si el usuario confirma "Fui yo", False si "No fui yo"
        
        Nota:
        Esto ayuda al analista a tomar una decisión informada.
        Si el usuario confirma (True), probablemente es legítima.
        Si el usuario rechaza (False), probablemente es fraude.
        """
        self.user_authenticated = confirmed
        self.user_auth_timestamp = datetime.now()

