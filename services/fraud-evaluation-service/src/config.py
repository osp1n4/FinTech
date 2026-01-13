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
    # ⚠️ IMPORTANTE: No usar valores por defecto en producción
    # Configurar mediante variables de entorno o secrets manager
    mongodb_url: str
    mongodb_database: str = "fraud_detection"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_ttl: int = 86400  # 24 horas

    # RabbitMQ
    # ⚠️ IMPORTANTE: No usar valores por defecto en producción
    # Configurar mediante variables de entorno o secrets manager
    rabbitmq_url: str
    rabbitmq_transactions_queue: str = "transactions"
    rabbitmq_manual_review_queue: str = "manual_review"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Fraud Rules
    amount_threshold: float = 1500.0
    location_radius_km: float = 100.0

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production-123456789"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # Email Configuration (Gmail SMTP)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "distribuidoraperrosgatos@gmail.com"
    smtp_password: str = "zwnd hwfd oirw yeje"
    from_email: str = "distribuidoraperrosgatos@gmail.com"
    base_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()

