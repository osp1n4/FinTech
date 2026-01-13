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
    IMPORTANTE: No incluir credenciales hardcodeadas por seguridad.
    """

    # MongoDB - SIN credenciales por defecto (deben venir de variables de entorno)
    mongodb_url: str
    mongodb_database: str = "fraud_detection"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_ttl: int = 86400  # 24 horas

    # RabbitMQ - SIN credenciales por defecto (deben venir de variables de entorno)
    rabbitmq_url: str
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
