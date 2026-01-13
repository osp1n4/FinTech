"""
Tests unitarios para UnusualTimeStrategy.

Verifica la detección de transacciones en horarios inusuales basándose
en patrones históricos del usuario. HU-007.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from decimal import Decimal
import sys
from pathlib import Path

# Agregar path al servicio (sin /src)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Transaction, Location, RiskLevel
from src.domain.strategies.unusual_time import UnusualTimeStrategy


class TestUnusualTimeStrategy:
    """Tests para la estrategia de horarios inusuales."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio de auditoría."""
        repo = Mock()
        repo.get_user_transaction_history = AsyncMock(return_value=[])
        return repo
    
    @pytest.fixture
    def strategy(self, mock_repository):
        """Instancia de la estrategia con repositorio mockeado."""
        return UnusualTimeStrategy(
            audit_repository=mock_repository,
            min_transactions_for_pattern=10,
            unusual_threshold_hours=3
        )
    
    @pytest.fixture
    def sample_transaction(self):
        """Transacción de ejemplo a las 14:00."""
        location = Location(latitude=4.7110, longitude=-74.0721)
        return Transaction(
            id="txn_001",
            user_id="user_123",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 11, 14, 0, 0)  # 14:00 (2 PM)
        )
    
    def test_insufficient_history_low_risk(self, strategy, mock_repository, sample_transaction):
        """Test: Sin suficiente historial, debe retornar LOW_RISK."""
        # Arrange
        # Simular historial insuficiente (menos de 10 transacciones)
        mock_transactions = [
            {"timestamp": datetime(2026, 1, i, 14, 0, 0)}
            for i in range(1, 6)  # Solo 5 transacciones
        ]
        strategy._get_user_transaction_history = lambda user_id: mock_transactions
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert result["reasons"] == []
        assert "Insufficient transaction history" in result["details"]
    
    def test_within_normal_hours_low_risk(self, strategy, sample_transaction):
        """Test: Transacción en horario normal debe ser LOW_RISK."""
        # Arrange
        # Simular historial con patrón de transacciones entre 13:00-15:00
        mock_transactions = [
            {"timestamp": datetime(2026, 1, i, 14, 0, 0)}
            for i in range(1, 15)  # 14 transacciones a las 14:00
        ]
        strategy._get_user_transaction_history = lambda user_id: mock_transactions
        strategy._analyze_hourly_pattern = lambda txs: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        strategy._is_unusual_hour = lambda hour, pattern: (False, 0)
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert result["reasons"] == []
        assert "within normal pattern" in result["details"]
    
    def test_moderately_unusual_time_medium_risk(self, strategy, sample_transaction):
        """Test: Horario moderadamente inusual debe ser MEDIUM_RISK."""
        # Arrange
        mock_transactions = [
            {"timestamp": datetime(2026, 1, i, 10, 0, 0)}
            for i in range(1, 15)  # Patrón normal a las 10:00
        ]
        strategy._get_user_transaction_history = lambda user_id: mock_transactions
        strategy._analyze_hourly_pattern = lambda txs: [0] * 24
        strategy._is_unusual_hour = lambda hour, pattern: (True, 4)  # 4 horas de desviación
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.MEDIUM_RISK
        assert "moderately_unusual_time" in result["reasons"]
        assert "4 hours from normal pattern" in result["details"]
    
    def test_highly_unusual_time_high_risk(self, strategy, sample_transaction):
        """Test: Horario altamente inusual debe ser HIGH_RISK."""
        # Arrange
        mock_transactions = [
            {"timestamp": datetime(2026, 1, i, 10, 0, 0)}
            for i in range(1, 15)  # Patrón normal a las 10:00
        ]
        strategy._get_user_transaction_history = lambda user_id: mock_transactions
        strategy._analyze_hourly_pattern = lambda txs: [0] * 24
        strategy._is_unusual_hour = lambda hour, pattern: (True, 8)  # 8 horas de desviación
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert "unusual_transaction_time" in result["reasons"]
        assert "8 hours from normal pattern" in result["details"]
    
    def test_midnight_transaction_detection(self, strategy):
        """Test: Transacciones de madrugada cuando el usuario normalmente opera de día."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        midnight_transaction = Transaction(
            id="txn_002",
            user_id="user_456",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 11, 3, 0, 0)  # 3:00 AM
        )
        
        # Simular patrón normal entre 9:00-18:00
        mock_transactions = [
            {"timestamp": datetime(2026, 1, i, (i % 9) + 9, 0, 0)}
            for i in range(1, 15)
        ]
        strategy._get_user_transaction_history = lambda user_id: mock_transactions
        strategy._analyze_hourly_pattern = lambda txs: [0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 3, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        strategy._is_unusual_hour = lambda hour, pattern: (True, 6)
        
        # Act
        result = strategy.evaluate(midnight_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert "unusual_transaction_time" in result["reasons"]
    
    def test_weekend_vs_weekday_pattern(self, strategy):
        """Test: Usuario con patrón diferente en fin de semana."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        # Sábado a las 22:00
        saturday_transaction = Transaction(
            id="txn_003",
            user_id="user_789",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 10, 22, 0, 0)  # Sábado 22:00
        )
        
        # Simular patrón de lunes a viernes 9:00-18:00
        weekday_transactions = []
        for day in range(5, 10):  # Lunes a Viernes
            for hour in range(9, 18):
                weekday_transactions.append({
                    "timestamp": datetime(2026, 1, day, hour, 0, 0)
                })
        
        strategy._get_user_transaction_history = lambda user_id: weekday_transactions[:15]
        strategy._analyze_hourly_pattern = lambda txs: [0] * 24
        strategy._is_unusual_hour = lambda hour, pattern: (True, 5)
        
        # Act
        result = strategy.evaluate(saturday_transaction)
        
        # Assert
        # Cambio de patrón weekday->weekend resulta en MEDIUM_RISK
        assert result["risk_level"] == RiskLevel.MEDIUM_RISK
    
    def test_consistent_late_night_user_low_risk(self, strategy):
        """Test: Usuario que consistentemente opera de noche debe ser LOW_RISK."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        night_transaction = Transaction(
            id="txn_004",
            user_id="user_night",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 11, 23, 0, 0)  # 23:00
        )
        
        # Simular patrón nocturno consistente (22:00-02:00)
        mock_transactions = [
            {"timestamp": datetime(2026, 1, i, 23, 0, 0)}
            for i in range(1, 15)
        ]
        strategy._get_user_transaction_history = lambda user_id: mock_transactions
        strategy._analyze_hourly_pattern = lambda txs: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 9]
        strategy._is_unusual_hour = lambda hour, pattern: (False, 0)
        
        # Act
        result = strategy.evaluate(night_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert result["reasons"] == []
    
    def test_strategy_name(self, strategy):
        """Test: Verificar que el nombre de la estrategia es correcto."""
        assert strategy.get_name() == "unusual_time"
    
    def test_custom_min_transactions_threshold(self, mock_repository):
        """Test: Debe permitir configurar el mínimo de transacciones para patrón."""
        # Arrange
        strategy = UnusualTimeStrategy(
            audit_repository=mock_repository,
            min_transactions_for_pattern=5,  # Reducido a 5
            unusual_threshold_hours=3
        )
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_005",
            user_id="user_custom",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 11, 14, 0, 0)
        )
        
        # 7 transacciones (suficiente con min=5)
        mock_transactions = [
            {"timestamp": datetime(2026, 1, i, 14, 0, 0)}
            for i in range(1, 8)
        ]
        strategy._get_user_transaction_history = lambda user_id: mock_transactions
        strategy._analyze_hourly_pattern = lambda txs: [0] * 24
        strategy._is_unusual_hour = lambda hour, pattern: (False, 0)
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        # No debe retornar "insufficient history" porque tiene 7 transacciones
        assert "Insufficient" not in result["details"]
    
    def test_custom_unusual_threshold_hours(self, mock_repository):
        """Test: Debe permitir configurar el umbral de horas inusuales."""
        # Arrange
        strategy = UnusualTimeStrategy(
            audit_repository=mock_repository,
            min_transactions_for_pattern=10,
            unusual_threshold_hours=2  # Umbral más estricto
        )
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_006",
            user_id="user_threshold",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 11, 14, 0, 0)
        )
        
        mock_transactions = [
            {"timestamp": datetime(2026, 1, i, 10, 0, 0)}
            for i in range(1, 15)
        ]
        strategy._get_user_transaction_history = lambda user_id: mock_transactions
        strategy._analyze_hourly_pattern = lambda txs: [0] * 24
        # 3 horas de desviación con threshold=2 → debería ser MEDIUM_RISK
        strategy._is_unusual_hour = lambda hour, pattern: (True, 3)
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.MEDIUM_RISK
    
    def test_exact_threshold_boundary_medium_risk(self, strategy):
        """Test: Desviación exacta en el umbral debe ser MEDIUM_RISK."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_007",
            user_id="user_boundary",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2026, 1, 11, 14, 0, 0)
        )
        
        mock_transactions = [
            {"timestamp": datetime(2026, 1, i, 10, 0, 0)}
            for i in range(1, 15)
        ]
        strategy._get_user_transaction_history = lambda user_id: mock_transactions
        strategy._analyze_hourly_pattern = lambda txs: [0] * 24
        strategy._is_unusual_hour = lambda hour, pattern: (True, 3)  # Exactamente en el umbral
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.MEDIUM_RISK
        assert "moderately_unusual_time" in result["reasons"]
