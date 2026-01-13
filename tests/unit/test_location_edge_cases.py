"""
Edge cases tests para el modelo Location.

GENERATED WITH GITHUB COPILOT
Prompt: "Generate comprehensive edge case tests for Location value object
including boundary coordinates, precision limits, and invalid inputs"

HUMAN REVIEW (Maria Paula Gutierrez):
Copilot generó estos tests automáticamente. Los revisé y agregué
algunos casos adicionales específicos para Colombia y casos de uso real.
"""
import pytest
import sys
from pathlib import Path

# Agregar path al servicio (sin /src)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Location


class TestLocationEdgeCases:
    """Casos límite y edge cases para Location."""
    
    # GENERATED WITH COPILOT: Geographic boundaries
    def test_north_pole_coordinates(self):
        """Test: North Pole (90°N) debe ser válido."""
        loc = Location(latitude=90.0, longitude=0.0)
        assert abs(loc.latitude - 90.0) < 1e-9
    
    def test_south_pole_coordinates(self):
        """Test: South Pole (-90°S) debe ser válido."""
        loc = Location(latitude=-90.0, longitude=0.0)
        assert abs(loc.latitude - (-90.0)) < 1e-9
    
    def test_equator_prime_meridian(self):
        """Test: Null Island (0°, 0°) debe ser válido."""
        loc = Location(latitude=0.0, longitude=0.0)
        assert abs(loc.latitude - 0.0) < 1e-9
        assert abs(loc.longitude - 0.0) < 1e-9
    
    def test_antimeridian_east(self):
        """Test: Antimeridian east (180°) debe ser válido."""
        loc = Location(latitude=0.0, longitude=180.0)
        assert abs(loc.longitude - 180.0) < 1e-9
    
    def test_antimeridian_west(self):
        """Test: Antimeridian west (-180°) debe ser válido."""
        loc = Location(latitude=0.0, longitude=-180.0)
        assert abs(loc.longitude - (-180.0)) < 1e-9
    
    # GENERATED WITH COPILOT: Precision edge cases
    def test_high_precision_gps_coordinates(self):
        """Test: Debe manejar precisión GPS de 6+ decimales (~10cm)."""
        loc = Location(latitude=4.7110050, longitude=-74.0720920)
        assert loc.latitude == pytest.approx(4.7110050, abs=1e-7)
        assert loc.longitude == pytest.approx(-74.0720920, abs=1e-7)
    
    def test_maximum_precision_coordinates(self):
        """Test: Debe manejar máxima precisión de Decimal."""
        loc = Location(latitude=4.71100501234567, longitude=-74.07209201234567)
        assert abs(loc.latitude - 4.71100501234567) < 1e-9
        assert abs(loc.longitude - (-74.07209201234567)) < 1e-9
    
    # GENERATED WITH COPILOT: Boundary violations
    def test_just_over_max_latitude(self):
        """Test: Debe rechazar latitud justo sobre 90°."""
        with pytest.raises(ValueError, match="[Ll]atitude"):
            Location(latitude=90.000001, longitude=0.0)
    
    def test_just_under_min_latitude(self):
        """Test: Debe rechazar latitud justo bajo -90°."""
        with pytest.raises(ValueError, match="[Ll]atitude"):
            Location(latitude=-90.000001, longitude=0.0)
    
    def test_just_over_max_longitude(self):
        """Test: Debe rechazar longitud justo sobre 180°."""
        with pytest.raises(ValueError, match="[Ll]ongitude"):
            Location(latitude=0.0, longitude=180.000001)
    
    def test_just_under_min_longitude(self):
        """Test: Debe rechazar longitud justo bajo -180°."""
        with pytest.raises(ValueError, match="[Ll]ongitude"):
            Location(latitude=0.0, longitude=-180.000001)
    
    def test_extremely_invalid_latitude(self):
        """Test: Debe rechazar valores extremadamente fuera de rango."""
        with pytest.raises(ValueError):
            Location(latitude=1000.0, longitude=0.0)
        
        with pytest.raises(ValueError):
            Location(latitude=-1000.0, longitude=0.0)
    
    def test_extremely_invalid_longitude(self):
        """Test: Debe rechazar longitudes extremadamente fuera de rango."""
        with pytest.raises(ValueError):
            Location(latitude=0.0, longitude=5000.0)
        
        with pytest.raises(ValueError):
            Location(latitude=0.0, longitude=-5000.0)
    
    # HUMAN REVIEW: Casos específicos de Colombia
    def test_colombia_major_cities(self):
        """Test: Coordenadas de ciudades principales de Colombia."""
        # Bogotá
        bogota = Location(latitude=4.7110, longitude=-74.0721)
        assert abs(bogota.latitude - 4.7110) < 1e-9
        
        # Medellín
        medellin = Location(latitude=6.2442, longitude=-75.5812)
        assert abs(medellin.latitude - 6.2442) < 1e-9
        
        # Cali
        cali = Location(latitude=3.4516, longitude=-76.5320)
        assert abs(cali.latitude - 3.4516) < 1e-9
        
        # Barranquilla
        barranquilla = Location(latitude=10.9685, longitude=-74.7813)
        assert abs(barranquilla.latitude - 10.9685) < 1e-9
    
    # GENERATED WITH COPILOT: Special numeric values
    def test_zero_coordinates(self):
        """Test: Coordenadas (0, 0) deben ser válidas."""
        loc = Location(latitude=0.0, longitude=0.0)
        assert abs(loc.latitude - 0.0) < 1e-9
        assert abs(loc.longitude - 0.0) < 1e-9
    
    def test_negative_zero_coordinates(self):
        """Test: -0.0 debe ser tratado igual que 0.0."""
        loc = Location(latitude=-0.0, longitude=-0.0)
        assert abs(loc.latitude - 0.0) < 1e-9
        assert abs(loc.longitude - 0.0) < 1e-9
    
    # GENERATED WITH COPILOT: Type validation
    def test_none_latitude_raises_error(self):
        """Test: None como latitud debe lanzar error."""
        with pytest.raises((TypeError, ValueError)):
            Location(latitude=None, longitude=0.0)
    
    def test_none_longitude_raises_error(self):
        """Test: None como longitud debe lanzar error."""
        with pytest.raises((TypeError, ValueError)):
            Location(latitude=0.0, longitude=None)
    
    def test_string_coordinates_raises_error(self):
        """Test: Strings no deben ser aceptados como coordenadas."""
        with pytest.raises(TypeError):
            Location(latitude="4.7110", longitude="-74.0721")
    
    # HUMAN REVIEW: Casos de uso fraudulento
    def test_impossible_travel_distances(self):
        """Test: Coordenadas para detectar viajes imposibles."""
        # Bogotá, Colombia
        loc1 = Location(latitude=4.7110, longitude=-74.0721)
        
        # Tokyo, Japan (imposible en 1 hora)
        loc2 = Location(latitude=35.6762, longitude=139.6503)
        
        # Ambas ubicaciones deben ser válidas
        assert abs(loc1.latitude - 4.7110) < 1e-9
        assert abs(loc2.latitude - 35.6762) < 1e-9
        
        # La lógica de "viaje imposible" se maneja en otra capa
        # Aquí solo validamos que las coordenadas son válidas


class TestLocationImmutability:
    """Tests para verificar inmutabilidad de Location."""
    
    # GENERATED WITH COPILOT: Immutability tests
    def test_cannot_modify_latitude(self):
        """Test: No se debe poder modificar latitude después de crear."""
        loc = Location(latitude=4.7110, longitude=-74.0721)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            loc.latitude = 10.0
    
    def test_cannot_modify_longitude(self):
        """Test: No se debe poder modificar longitude después de crear."""
        loc = Location(latitude=4.7110, longitude=-74.0721)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            loc.longitude = -80.0
    
    def test_cannot_add_new_attributes(self):
        """Test: No se deben poder agregar atributos nuevos."""
        loc = Location(latitude=4.7110, longitude=-74.0721)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            loc.new_attribute = "value"
