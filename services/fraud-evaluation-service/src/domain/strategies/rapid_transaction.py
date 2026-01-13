"""
RapidTransactionStrategy - Detecta múltiples transacciones rápidas.
HU-006: Como sistema, quiero detectar si un usuario realiza más de 3 transacciones
en 5 minutos para marcar como sospechoso.
"""
from datetime import datetime, timedelta
from typing import Dict, Any

from .base import FraudStrategy
from src.domain.models import Transaction, RiskLevel


class RapidTransactionStrategy(FraudStrategy):
    """
    Estrategia que detecta múltiples transacciones rápidas en un período corto.
    
    Utiliza Redis para rastrear transacciones recientes por usuario y detecta
    patrones de transacciones rápidas que puedan indicar fraude.
    """
    
    def __init__(self, redis_client, max_transactions: int = 3, window_minutes: int = 5):
        """
        Inicializa la estrategia con el cliente Redis y parámetros de detección.
        
        Args:
            redis_client: Cliente Redis para almacenar transacciones recientes
            max_transactions: Número máximo de transacciones permitidas en la ventana
            window_minutes: Tamaño de la ventana de tiempo en minutos
        """
        self.redis_client = redis_client
        self.max_transactions = max_transactions
        self.window_minutes = window_minutes
        self.window_seconds = window_minutes * 60
    
    def get_name(self) -> str:
        """Retorna el nombre de la estrategia."""
        return "rapid_transaction"
    
    def evaluate(self, transaction: Transaction, historical_location=None) -> Dict[str, Any]:
        """
        Evalúa si la transacción es parte de un patrón de transacciones rápidas.
        
        Args:
            transaction: La transacción a evaluar
            historical_location: No usado en esta estrategia
            
        Returns:
            Dict con risk_level, reasons y details
        """
        try:
            user_id = transaction.user_id
            current_time = transaction.timestamp
            
            # Clave de Redis para este usuario
            redis_key = f"rapid_tx:{user_id}"
            
            # Añadir la transacción actual PRIMERO
            self.redis_client.zadd(
                redis_key,
                {transaction.id: current_time.timestamp()}
            )
            
            # Establecer expiración de la clave
            self.redis_client.expire(redis_key, self.window_seconds)
            
            # Limpiar transacciones antiguas
            self.redis_client.zremrangebyscore(
                redis_key,
                0,
                current_time.timestamp() - self.window_seconds
            )
            
            # Contar transacciones en la ventana (incluyendo la actual que acabamos de añadir)
            transaction_count = self.redis_client.zcount(
                redis_key,
                current_time.timestamp() - self.window_seconds,
                current_time.timestamp()
            )
            
            # Evaluar riesgo según el número de transacciones
            # Solo mostrar violación cuando se SUPERA el límite
            if transaction_count > self.max_transactions:
                return {
                    "risk_level": RiskLevel.HIGH_RISK,
                    "reasons": ["rapid_transactions_detected"],
                    "details": f"{transaction_count} transactions in {self.window_minutes} minutes (limit: {self.max_transactions})"
                }
            else:
                # 3 o menos transacciones = OK (sin violación)
                return {
                    "risk_level": RiskLevel.LOW_RISK,
                    "reasons": [],
                    "details": f"{transaction_count} transactions in {self.window_minutes} minutes"
                }
                
        except Exception as e:
            # En caso de error con Redis, retornar riesgo bajo para no bloquear
            print(f"Error en RapidTransactionStrategy: {e}")
            return {
                "risk_level": RiskLevel.LOW_RISK,
                "reasons": ["rapid_transaction_check_failed"],
                "details": "Could not check rapid transactions"
            }
    
    def get_reason(self, risk_level: RiskLevel) -> str:
        """
        Retorna la razón del nivel de riesgo asignado.
        
        Args:
            risk_level: El nivel de riesgo asignado
            
        Returns:
            str: Descripción del motivo del riesgo
        """
        if risk_level == RiskLevel.HIGH_RISK:
            return (
                f"Se detectaron más de {self.max_transactions} transacciones "
                f"en {self.window_minutes} minutos"
            )
        elif risk_level == RiskLevel.MEDIUM_RISK:
            return (
                f"Se detectaron {self.max_transactions} transacciones "
                f"en {self.window_minutes} minutos (límite alcanzado)"
            )
        else:
            return "Patrón de transacciones normal"

