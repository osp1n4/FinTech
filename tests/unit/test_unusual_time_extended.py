"""
Tests extendidos para UnusualTimeStrategy - Aumentar cobertura.

Cubre casos edge y métodos internos no cubiertos por tests básicos.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from decimal import Decimal
import sys
from pathlib import Path

# Agregar path al servicio
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Transaction, Location, RiskLevel
from src.domain.strategies.unusual_time import UnusualTimeStrategy


class TestUnusualTimeExtended:
    """Tests extendidos para métodos internos y casos edge."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio."""
        repo = Mock()
        repo.get_evaluations_by_user = AsyncMock(return_value=[])
        return repo
    
    @pytest.fixture
    def strategy(self, mock_repository):
        """Instancia de la estrategia."""
        return UnusualTimeStrategy(
            audit_repository=mock_repository,
            min_transactions_for_pattern=10,
            unusual_threshold_hours=3
        )
    
    def test_analyze_hourly_pattern_with_objects(self, strategy):
        """Test: Analizar patrón con objetos que tienen timestamp."""
        # Arrange
        evaluations = [
            type('obj', (object,), {'timestamp': datetime(2026, 1, i, 14, 0, 0)})()
            for i in range(1, 11)
        ]
        
        # Act
        pattern = strategy._analyze_hourly_pattern(evaluations)
        
        # Assert
        assert isinstance(pattern, dict)
        assert 14 in pattern
        assert pattern[14] == 10
    
    def test_analyze_hourly_pattern_with_dicts(self, strategy):
        """Test: Analizar patrón con diccionarios."""
        # Arrange
        transactions = [
            {"timestamp": datetime(2026, 1, i, 15, 0, 0)}
            for i in range(1, 6)
        ]
        
        # Act
        pattern = strategy._analyze_hourly_pattern(transactions)
        
        # Assert
        assert 15 in pattern
        assert pattern[15] == 5
    
    def test_analyze_hourly_pattern_with_iso_strings(self, strategy):
        """Test: Analizar patrón con strings ISO."""
        # Arrange
        transactions = [
            {"timestamp": "2026-01-11T16:00:00+00:00"},
            {"timestamp": "2026-01-12T16:30:00+00:00"},
            {"timestamp": "2026-01-13T16:45:00+00:00"}
        ]
        
        # Act
        pattern = strategy._analyze_hourly_pattern(transactions)
        
        # Assert
        assert 16 in pattern
        assert pattern[16] == 3
    
    def test_analyze_hourly_pattern_with_invalid_data(self, strategy):
        """Test: Analizar patrón con datos inválidos."""
        # Arrange
        transactions = [
            {"timestamp": "invalid"},
            {"no_timestamp": "data"},
            None
        ]
        
        # Act
        pattern = strategy._analyze_hourly_pattern(transactions)
        
        # Assert - Debe retornar diccionario vacío o con datos válidos únicamente
        assert isinstance(pattern, dict)
    
    def test_is_unusual_hour_empty_pattern(self, strategy):
        """Test: Hora inusual con patrón vacío."""
        # Act
        is_unusual, deviation = strategy._is_unusual_hour(14, {})
        
        # Assert
        assert is_unusual is False
        assert deviation == 0
    
    def test_is_unusual_hour_never_used_close(self, strategy):
        """Test: Hora nunca usada pero cerca de horas usadas."""
        # Arrange - Usuario siempre transacciona a las 10:00
        pattern = {10: 20}
        
        # Act - Transacción a las 13:00 (3 horas de diferencia)
        is_unusual, deviation = strategy._is_unusual_hour(13, pattern)
        
        # Assert
        assert is_unusual is True
        assert deviation == 3
    
    def test_is_unusual_hour_never_used_wrap_around(self, strategy):
        """Test: Hora nunca usada con wrap-around (cruce de medianoche)."""
        # Arrange - Usuario transacciona a las 23:00
        pattern = {23: 10}
        
        # Act - Transacción a las 2:00 (3 horas después, cruzando medianoche)
        _, deviation = strategy._is_unusual_hour(2, pattern)
        
        # Assert - La desviación mínima debería ser 3
        assert deviation >= 3
    
    def test_is_unusual_hour_low_frequency(self, strategy):
        """Test: Hora con frecuencia <5%."""
        # Arrange - 1 de 100 transacciones = 1% < 5%
        pattern = {14: 1, 10: 99}
        
        # Act
        is_unusual, _ = strategy._is_unusual_hour(14, pattern)
        
        # Assert
        assert is_unusual is True
    
    def test_is_unusual_hour_high_frequency(self, strategy):
        """Test: Hora con frecuencia alta (>5%)."""
        # Arrange - 20 de 100 = 20% > 5%
        pattern = {14: 20, 10: 80}
        
        # Act
        is_unusual, deviation = strategy._is_unusual_hour(14, pattern)
        
        # Assert
        assert is_unusual is False
        assert deviation == 0
    
    def test_get_reason_high_risk(self, strategy):
        """Test: Razón para HIGH_RISK."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_001",
            user_id="user_123",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 11, 14, 0, 0)
        )
        
        # Act
        reason = strategy.get_reason(transaction, RiskLevel.HIGH_RISK)
        
        # Assert
        assert "muy inusual" in reason.lower()
        assert "14:00" in reason
    
    def test_get_reason_medium_risk(self, strategy):
        """Test: Razón para MEDIUM_RISK."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_001",
            user_id="user_123",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 11, 14, 0, 0)
        )
        
        # Act
        reason = strategy.get_reason(transaction, RiskLevel.MEDIUM_RISK)
        
        # Assert
        assert "moderadamente inusual" in reason.lower()
    
    def test_get_reason_low_risk(self, strategy):
        """Test: Razón para LOW_RISK."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_001",
            user_id="user_123",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 11, 14, 0, 0)
        )
        
        # Act
        reason = strategy.get_reason(transaction, RiskLevel.LOW_RISK)
        
        # Assert
        assert "dentro del patrón normal" in reason.lower()
    
    def test_evaluate_with_exception(self, strategy):
        """Test: Manejo de excepciones en evaluate."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_001",
            user_id="user_123",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 11, 14, 0, 0)
        )
        
        # Forzar excepción
        def raise_error(user_id):
            raise ValueError("Test error")
        
        strategy._get_user_transaction_history = raise_error
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert "unusual_time_check_failed" in result["reasons"]
    
    def test_get_user_transaction_history_with_exception(self, strategy, mock_repository):
        """Test: Excepciones en get_user_transaction_history."""
        # Arrange
        mock_repository.get_evaluations_by_user = AsyncMock(side_effect=Exception("DB error"))
        
        # Act
        result = strategy._get_user_transaction_history("user_001")
        
        # Assert
        assert result == []

