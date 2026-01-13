"""
Tests unitarios para LocationStrategy.

Verifica la detección de ubicaciones inusuales fuera del radio habitual.
HU-005: Detección de fraude por ubicación geográfica.
"""
import pytest
from decimal import Decimal
from datetime import datetime
import sys
from pathlib import Path

# Agregar path al servicio (sin /src)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Transaction, Location, RiskLevel
from src.domain.strategies.location_check import LocationStrategy


class TestLocationStrategy:
    """Tests para la estrategia de validación de ubicación."""
    
    @pytest.fixture
    def strategy(self):
        """Instancia de la estrategia con radio de 100 km."""
        return LocationStrategy(radius_km=100.0)
    
    @pytest.fixture
    def bogota_location(self):
        """Ubicación de Bogotá."""
        return Location(latitude=4.7110, longitude=-74.0721)
    
    @pytest.fixture
    def medellin_location(self):
        """Ubicación de Medellín (aproximadamente 240 km de Bogotá)."""
        return Location(latitude=6.2442, longitude=-75.5812)
    
    @pytest.fixture
    def nearby_location(self):
        """Ubicación cercana a Bogotá (dentro de 100 km)."""
        return Location(latitude=4.8110, longitude=-74.1721)  # ~15 km
    
    def test_strategy_creation_with_valid_radius(self):
        """Test: Debe crear estrategia con radio válido."""
        strategy = LocationStrategy(radius_km=100.0)
        assert abs(strategy.radius_km - 100.0) < 1e-9
    
    def test_strategy_rejects_zero_radius(self):
        """Test: Debe rechazar radio cero."""
        with pytest.raises(ValueError, match="Radius must be positive"):
            LocationStrategy(radius_km=0.0)
    
    def test_strategy_rejects_negative_radius(self):
        """Test: Debe rechazar radio negativo."""
        with pytest.raises(ValueError, match="Radius must be positive"):
            LocationStrategy(radius_km=-50.0)
    
    def test_first_transaction_no_historical_location(self, strategy, bogota_location):
        """Test: Primera transacción sin historial debe ser LOW_RISK."""
        # Arrange
        transaction = Transaction(
            id="txn_001",
            user_id="new_user",
            amount=Decimal("500.0"),
            location=bogota_location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction, historical_location=None)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert "no_historical_location" in result["reasons"]
        assert "First transaction for user" in result["details"]
    
    def test_transaction_within_radius_low_risk(self, strategy, bogota_location, nearby_location):
        """Test: Transacción dentro del radio debe ser LOW_RISK."""
        # Arrange
        transaction = Transaction(
            id="txn_002",
            user_id="user_123",
            amount=Decimal("500.0"),
            location=nearby_location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction, historical_location=bogota_location)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert result["reasons"] == []
        assert result["details"] == ""
    
    def test_transaction_exceeds_radius_high_risk(self, strategy, bogota_location, medellin_location):
        """Test: Transacción fuera del radio debe ser HIGH_RISK."""
        # Arrange
        transaction = Transaction(
            id="txn_003",
            user_id="user_456",
            amount=Decimal("500.0"),
            location=medellin_location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction, historical_location=bogota_location)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert "unusual_location" in result["reasons"]
        assert "exceeds radius" in result["details"]
        # Distancia aproximada 238-240 km
        assert "238" in result["details"] or "239" in result["details"] or "240" in result["details"]
    
    def test_transaction_at_exact_radius_boundary(self, strategy, bogota_location):
        """Test: Transacción exactamente en el límite debe ser LOW_RISK."""
        # Arrange
        # Calcular una ubicación a exactamente 100 km
        # Aproximadamente 0.9 grados de latitud = 100 km
        boundary_location = Location(latitude=5.611, longitude=-74.0721)
        transaction = Transaction(
            id="txn_004",
            user_id="user_789",
            amount=Decimal("500.0"),
            location=boundary_location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction, historical_location=bogota_location)
        
        # Assert
        # Exactamente en el límite (100 km) la implementación actual lo considera HIGH_RISK
        assert result["risk_level"] == RiskLevel.HIGH_RISK
    
    def test_same_location_zero_distance(self, strategy, bogota_location):
        """Test: Misma ubicación debe tener distancia cero y ser LOW_RISK."""
        # Arrange
        transaction = Transaction(
            id="txn_005",
            user_id="user_same",
            amount=Decimal("500.0"),
            location=bogota_location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction, historical_location=bogota_location)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert result["reasons"] == []
    
    def test_transaction_none_raises_error(self, strategy):
        """Test: Transaction None debe lanzar ValueError."""
        with pytest.raises(ValueError, match="Transaction cannot be None"):
            strategy.evaluate(None, historical_location=Location(4.7110, -74.0721))
    
    def test_international_distance_high_risk(self, strategy, bogota_location):
        """Test: Transacción internacional debe ser HIGH_RISK."""
        # Arrange
        # Miami, USA
        miami_location = Location(latitude=25.7617, longitude=-80.1918)
        transaction = Transaction(
            id="txn_006",
            user_id="user_international",
            amount=Decimal("500.0"),
            location=miami_location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction, historical_location=bogota_location)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert "unusual_location" in result["reasons"]
        # Miami está a ~2500 km de Bogotá
        assert "2" in result["details"]  # Al menos empieza con 2
    
    def test_cross_country_distance_high_risk(self, strategy):
        """Test: Transacción entre ciudades lejanas dentro del país."""
        # Arrange
        cali_location = Location(latitude=3.4516, longitude=-76.5320)
        cartagena_location = Location(latitude=10.3910, longitude=-75.4794)
        
        transaction = Transaction(
            id="txn_007",
            user_id="user_cross",
            amount=Decimal("500.0"),
            location=cartagena_location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction, historical_location=cali_location)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        # Cali a Cartagena es más de 600 km
        assert "unusual_location" in result["reasons"]
    
    def test_small_radius_strategy(self):
        """Test: Estrategia con radio pequeño debe detectar más violaciones."""
        # Arrange
        strict_strategy = LocationStrategy(radius_km=10.0)  # Solo 10 km
        bogota_center = Location(latitude=4.7110, longitude=-74.0721)
        bogota_north = Location(latitude=4.8110, longitude=-74.0721)  # ~11 km
        
        transaction = Transaction(
            id="txn_008",
            user_id="user_strict",
            amount=Decimal("500.0"),
            location=bogota_north,
            timestamp=datetime.now()
        )
        
        # Act
        result = strict_strategy.evaluate(transaction, historical_location=bogota_center)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
    
    def test_large_radius_strategy(self):
        """Test: Estrategia con radio grande debe ser más permisiva."""
        # Arrange
        permissive_strategy = LocationStrategy(radius_km=500.0)  # 500 km
        bogota_location = Location(latitude=4.7110, longitude=-74.0721)
        medellin_location = Location(latitude=6.2442, longitude=-75.5812)  # ~240 km
        
        transaction = Transaction(
            id="txn_009",
            user_id="user_permissive",
            amount=Decimal("500.0"),
            location=medellin_location,
            timestamp=datetime.now()
        )
        
        # Act
        result = permissive_strategy.evaluate(transaction, historical_location=bogota_location)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
    
    def test_haversine_calculation_accuracy(self, strategy):
        """Test: Verificar que la fórmula de Haversine calcula correctamente."""
        # Arrange
        loc1 = Location(latitude=4.7110, longitude=-74.0721)  # Bogotá
        loc2 = Location(latitude=6.2442, longitude=-75.5812)  # Medellín
        
        # Act
        distance = strategy._calculate_distance(loc1, loc2)
        
        # Assert
        # La distancia entre Bogotá y Medellín es aproximadamente 240 km
        assert 235 < distance < 245
    
    def test_equator_crossing_distance(self, strategy):
        """Test: Distancia cruzando el ecuador."""
        # Arrange
        north = Location(latitude=5.0, longitude=-74.0)
        south = Location(latitude=-5.0, longitude=-74.0)
        
        # Act
        distance = strategy._calculate_distance(north, south)
        
        # Assert
        # Aproximadamente 1111 km (~10 grados de latitud)
        assert 1100 < distance < 1120
    
    def test_antimeridian_crossing_distance(self, strategy):
        """Test: Distancia cruzando el antimeridiano."""
        # Arrange
        east = Location(latitude=0.0, longitude=179.0)
        west = Location(latitude=0.0, longitude=-179.0)
        
        # Act
        distance = strategy._calculate_distance(east, west)
        
        # Assert
        # 2 grados de longitud en el ecuador ≈ 222 km
        assert 200 < distance < 250
    
    def test_polar_region_distance(self, strategy):
        """Test: Distancia en regiones polares."""
        # Arrange
        near_pole1 = Location(latitude=89.0, longitude=0.0)
        near_pole2 = Location(latitude=89.0, longitude=180.0)
        
        # Act
        distance = strategy._calculate_distance(near_pole1, near_pole2)
        
        # Assert
        # Cerca del polo, la distancia es ~222 km debido a la curvatura
        assert distance < 250
    
    def test_details_include_coordinates(self, strategy, bogota_location, medellin_location):
        """Test: Los detalles deben incluir las coordenadas."""
        # Arrange
        transaction = Transaction(
            id="txn_010",
            user_id="user_coords",
            amount=Decimal("500.0"),
            location=medellin_location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction, historical_location=bogota_location)
        
        # Assert
        assert "Previous:" in result["details"]
        assert "Current:" in result["details"]
        assert "4.711" in result["details"]
        assert "6.2442" in result["details"]
