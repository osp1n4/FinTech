"""
Infrastructure - Configuración centralizada
Manejo de variables de entorno y settings

Cumple Single Responsibility: Solo gestiona configuración

Nota del desarrollador (María Gutiérrez):
La IA sugirió leer variables de entorno directamente en cada adaptador.
Lo centralicé en un módulo de configuración usando Pydantic Settings
para cumplir con "Don't Repeat Yourself" y facilitar testing.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración de la aplicación desde variables de entorno
    
    Usa Pydantic para validación automática y valores por defecto
    """

    # MongoDB
    mongodb_url: str = "mongodb://admin:fraud2026@localhost:27017"
    mongodb_database: str = "fraud_detection"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_ttl: int = 86400  # 24 horas

    # RabbitMQ
    rabbitmq_url: str = "amqp://fraud:fraud2026@localhost:5672"
    rabbitmq_transactions_queue: str = "transactions"
    rabbitmq_manual_review_queue: str = "manual_review"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Fraud Rules
    amount_threshold: float = 1500.0
    location_radius_km: float = 100.0

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()
