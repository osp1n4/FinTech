"""
Tests Unitarios para el Modelo Admin
Siguiendo metodología TDD (Test-Driven Development)

Cumplimiento SOLID en tests:
- Single Responsibility: Cada test verifica un único comportamiento
- Open/Closed: Tests extensibles para nuevas validaciones
- Dependency Inversion: Tests no dependen de implementaciones concretas

Coverage objetivo: >70%
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio services al path
services_path = Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service" / "src"
sys.path.insert(0, str(services_path))

from domain.models import Admin


class TestAdminCreation:
    """Tests para creación válida de entidad Admin"""
    
    def test_admin_creation_valid(self):
        """
        TEST-ADMIN-001: Crear Admin con datos válidos
        
        Given: Datos válidos de administrador
        When: Se crea una instancia de Admin
        Then: Admin se crea correctamente con todos los campos
        """
        # Arrange
        admin_id = "admin_john"
        email = "john@admin.com"
        hashed_password = "$2b$12$hashed_password_here"
        full_name = "John Admin"
        
        # Act
        admin = Admin(
            admin_id=admin_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        
        # Assert
        assert admin.admin_id == admin_id
        assert admin.email == email
        assert admin.hashed_password == hashed_password
        assert admin.full_name == full_name
        assert admin.is_active is True  # Default value
        assert admin.is_verified is False  # Default value
        assert admin.verification_token is None
        assert admin.verification_token_expires is None
        assert admin.last_login is None
        assert isinstance(admin.created_at, datetime)


class TestAdminValidation:
    """Tests para validaciones del modelo Admin"""
    
    def test_admin_id_validation_min_length(self):
        """
        TEST-ADMIN-002: Validar formato de admin_id (mínimo 3 caracteres)
        
        Given: admin_id con menos de 3 caracteres
        When: Se intenta crear Admin
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError, match="admin_id must be at least 3 characters"):
            Admin(
                admin_id="ab",  # Solo 2 caracteres
                email="test@admin.com",
                hashed_password="$2b$12$hash",
                full_name="Test Admin"
            )
    
    def test_admin_id_validation_format(self):
        """
        TEST-ADMIN-003: Validar formato de admin_id (solo alfanuméricos y guiones bajos)
        
        Given: admin_id con caracteres inválidos
        When: Se intenta crear Admin
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError, match="admin_id can only contain letters, numbers, and underscores"):
            Admin(
                admin_id="admin-john!",  # Contiene caracteres especiales
                email="test@admin.com",
                hashed_password="$2b$12$hash",
                full_name="Test Admin"
            )
    
    def test_email_format_validation(self):
        """
        TEST-ADMIN-004: Validar formato de email
        
        Given: Email con formato inválido
        When: Se intenta crear Admin
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError, match="Invalid email format"):
            Admin(
                admin_id="admin_test",
                email="invalid_email",  # Sin @
                hashed_password="$2b$12$hash",
                full_name="Test Admin"
            )
    
    def test_full_name_validation_min_length(self):
        """
        TEST-ADMIN-005: Validar full_name (mínimo 2 caracteres)
        
        Given: full_name con menos de 2 caracteres
        When: Se intenta crear Admin
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError, match="full_name must be at least 2 characters"):
            Admin(
                admin_id="admin_test",
                email="test@admin.com",
                hashed_password="$2b$12$hash",
                full_name="A"  # Solo 1 carácter
            )
    
    def test_admin_id_validation_empty(self):
        """
        TEST-ADMIN-006: Validar que admin_id no puede estar vacío
        
        Given: admin_id vacío
        When: Se intenta crear Admin
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError, match="Admin ID cannot be empty"):
            Admin(
                admin_id="",
                email="test@admin.com",
                hashed_password="$2b$12$hash",
                full_name="Test Admin"
            )
    
    def test_admin_id_validation_whitespace(self):
        """
        TEST-ADMIN-007: Validar que admin_id no puede ser solo espacios
        
        Given: admin_id con solo espacios
        When: Se intenta crear Admin
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError, match="Admin ID cannot be empty"):
            Admin(
                admin_id="   ",
                email="test@admin.com",
                hashed_password="$2b$12$hash",
                full_name="Test Admin"
            )
    
    def test_hashed_password_validation_empty(self):
        """
        TEST-ADMIN-008: Validar que hashed_password no puede estar vacío
        
        Given: hashed_password vacío
        When: Se intenta crear Admin
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError, match="Hashed password cannot be empty"):
            Admin(
                admin_id="admin_test",
                email="test@admin.com",
                hashed_password="",
                full_name="Test Admin"
            )
    
    def test_full_name_validation_empty(self):
        """
        TEST-ADMIN-009: Validar que full_name no puede estar vacío
        
        Given: full_name vacío
        When: Se intenta crear Admin
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError, match="Full name cannot be empty"):
            Admin(
                admin_id="admin_test",
                email="test@admin.com",
                hashed_password="$2b$12$hash",
                full_name=""
            )


class TestAdminDefaults:
    """Tests para valores por defecto de Admin"""
    
    def test_admin_defaults(self):
        """
        TEST-ADMIN-006: Verificar valores por defecto (is_active, is_verified)
        
        Given: Admin creado sin especificar valores opcionales
        When: Se accede a campos con valores por defecto
        Then: Los valores por defecto son correctos
        """
        admin = Admin(
            admin_id="admin_test",
            email="test@admin.com",
            hashed_password="$2b$12$hash",
            full_name="Test Admin"
        )
        
        assert admin.is_active is True
        assert admin.is_verified is False
        assert admin.verification_token is None
        assert admin.verification_token_expires is None
        assert admin.last_login is None
        assert isinstance(admin.created_at, datetime)


class TestAdminSerialization:
    """Tests para conversión de Admin a dict para MongoDB"""
    
    def test_admin_to_dict_for_mongodb(self):
        """
        TEST-ADMIN-007: Verificar conversión a dict para MongoDB
        
        Given: Una instancia de Admin
        When: Se convierte a diccionario para MongoDB
        Then: El diccionario contiene todos los campos necesarios y no incluye hashed_password
        """
        admin = Admin(
            admin_id="admin_test",
            email="test@admin.com",
            hashed_password="$2b$12$hash",
            full_name="Test Admin"
        )
        
        admin_dict = admin.to_dict()
        
        assert admin_dict["admin_id"] == "admin_test"
        assert admin_dict["email"] == "test@admin.com"
        assert "hashed_password" not in admin_dict  # No debe incluir password
        assert admin_dict["full_name"] == "Test Admin"
        assert admin_dict["is_active"] is True
        assert admin_dict["is_verified"] is False
        assert admin_dict["verification_token"] is None
        assert admin_dict["verification_token_expires"] is None
        assert admin_dict["last_login"] is None
        assert admin_dict["created_at"] is not None
    
    def test_admin_to_dict_with_last_login(self):
        """
        TEST-ADMIN-010: Verificar conversión a dict cuando last_login tiene valor
        
        Given: Una instancia de Admin con last_login definido
        When: Se convierte a diccionario para MongoDB
        Then: El diccionario incluye last_login serializado correctamente
        """
        last_login_time = datetime(2024, 1, 15, 10, 30, 0)
        admin = Admin(
            admin_id="admin_test",
            email="test@admin.com",
            hashed_password="$2b$12$hash",
            full_name="Test Admin",
            last_login=last_login_time
        )
        
        admin_dict = admin.to_dict()
        
        assert admin_dict["last_login"] == last_login_time.isoformat()
        assert "hashed_password" not in admin_dict


class TestAdminImmutability:
    """Tests para verificar comportamiento de campos después de creación"""
    
    def test_admin_created_at_auto_generated(self):
        """
        TEST-ADMIN-008: Verificar que created_at se genera automáticamente
        
        Given: Admin creado sin especificar created_at
        When: Se accede al campo created_at
        Then: created_at tiene un valor datetime actual
        """
        before = datetime.now()
        admin = Admin(
            admin_id="admin_test",
            email="test@admin.com",
            hashed_password="$2b$12$hash",
            full_name="Test Admin"
        )
        after = datetime.now()
        
        assert before <= admin.created_at <= after
