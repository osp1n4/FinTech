"""
Tests unitarios para el módulo de configuración.

Valida que Settings lee correctamente las variables de entorno
y tiene valores por defecto apropiados.
"""
import pytest
import os
import sys
from pathlib import Path

# Agregar path al servicio
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.config import Settings


class TestSettings:
    """Tests para la clase Settings."""
    
    def test_settings_default_mongodb_url(self):
        """Test: Verificar URL por defecto de MongoDB."""
        settings = Settings()
        assert settings.mongodb_url.startswith("mongodb://")
        assert "27017" in settings.mongodb_url
    
    def test_settings_default_mongodb_database(self):
        """Test: Verificar nombre por defecto de base de datos."""
        settings = Settings()
        assert settings.mongodb_database == "fraud_detection"
        assert len(settings.mongodb_database) > 0
    
    def test_settings_default_redis_url(self):
        """Test: Verificar URL por defecto de Redis."""
        settings = Settings()
        assert settings.redis_url.startswith("redis://")
        assert "6379" in settings.redis_url
    
    def test_settings_default_redis_ttl(self):
        """Test: Verificar TTL por defecto de Redis (24 horas)."""
        settings = Settings()
        assert settings.redis_ttl == 86400
        assert isinstance(settings.redis_ttl, int)
    
    def test_settings_default_rabbitmq_url(self):
        """Test: Verificar URL por defecto de RabbitMQ."""
        settings = Settings()
        assert settings.rabbitmq_url.startswith("amqp://")
        assert "5672" in settings.rabbitmq_url
    
    def test_settings_default_rabbitmq_queues(self):
        """Test: Verificar nombres por defecto de colas RabbitMQ."""
        settings = Settings()
        assert settings.rabbitmq_transactions_queue == "transactions"
        assert settings.rabbitmq_manual_review_queue == "manual_review"
    
    def test_settings_default_api_host(self):
        """Test: Verificar host por defecto de API."""
        settings = Settings()
        assert settings.api_host == "0.0.0.0"
    
    def test_settings_default_api_port(self):
        """Test: Verificar puerto por defecto de API."""
        settings = Settings()
        assert settings.api_port == 8000
        assert isinstance(settings.api_port, int)
    
    def test_settings_default_amount_threshold(self):
        """Test: Verificar umbral por defecto de monto."""
        settings = Settings()
        assert abs(settings.amount_threshold - 1500.0) < 0.001
        assert isinstance(settings.amount_threshold, float)
        assert settings.amount_threshold > 0
    
    def test_settings_default_location_radius(self):
        """Test: Verificar radio por defecto de ubicación."""
        settings = Settings()
        assert abs(settings.location_radius_km - 100.0) < 0.001
        assert isinstance(settings.location_radius_km, float)
        assert settings.location_radius_km > 0
    
    def test_settings_from_env_mongodb_url(self, monkeypatch):
        """Test: Leer MONGODB_URL desde variable de entorno."""
        test_url = "mongodb://testuser:testpass@testhost:27017"
        monkeypatch.setenv("MONGODB_URL", test_url)
        settings = Settings()
        assert settings.mongodb_url == test_url
    
    def test_settings_from_env_api_port(self, monkeypatch):
        """Test: Leer API_PORT desde variable de entorno."""
        monkeypatch.setenv("API_PORT", "9000")
        settings = Settings()
        assert settings.api_port == 9000
    
    def test_settings_from_env_amount_threshold(self, monkeypatch):
        """Test: Leer AMOUNT_THRESHOLD desde variable de entorno."""
        monkeypatch.setenv("AMOUNT_THRESHOLD", "2000.0")
        settings = Settings()
        assert abs(settings.amount_threshold - 2000.0) < 0.001
    
    def test_settings_case_insensitive(self, monkeypatch):
        """Test: Configuración es case-insensitive."""
        monkeypatch.setenv("mongodb_database", "test_db_lower")
        settings = Settings()
        assert settings.mongodb_database == "test_db_lower"
    
    def test_settings_config_class_exists(self):
        """Test: Verificar que existe la clase Config interna."""
        _ = Settings()
        assert hasattr(Settings, 'Config')
        assert hasattr(Settings.Config, 'env_file')
        assert Settings.Config.env_file == ".env"
        assert Settings.Config.case_sensitive is False
