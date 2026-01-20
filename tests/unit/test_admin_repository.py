"""
Tests Unitarios para AdminRepository
Siguiendo metodología TDD (Test-Driven Development)

Cumplimiento SOLID en tests:
- Single Responsibility: Cada test verifica un único comportamiento
- Open/Closed: Tests extensibles para nuevas operaciones CRUD
- Dependency Inversion: Tests usan mocks para no depender de MongoDB real

Coverage objetivo: >70%
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Agregar el directorio services al path
services_path = Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service" / "src"
sys.path.insert(0, str(services_path))

from domain.models import Admin
from infrastructure.admin_repository import AdminRepository


class TestAdminRepositoryInit:
    """Tests para inicialización del repositorio"""
    
    def test_repository_initialization(self):
        """
        TEST-REPO-001: Verificar inicialización correcta del repositorio
        
        Given: Credenciales de conexión a MongoDB
        When: Se crea una instancia de AdminRepository
        Then: El repositorio se inicializa con conexión y colección correctas
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            # Verificar que se creó el cliente
            mock_client.assert_called_once_with("mongodb://localhost:27017")
            
            # Verificar que se accedió a la base de datos correcta
            mock_client.return_value.__getitem__.assert_called_with("test_db")
            
            # Verificar que se crearon los índices
            assert mock_db.admins.create_index.call_count == 3


class TestAdminRepositorySave:
    """Tests para guardado de administradores"""
    
    def test_save_admin(self):
        """
        TEST-REPO-002: Guardar admin en MongoDB
        
        Given: Una instancia válida de Admin
        When: Se llama a save_admin
        Then: El admin se guarda en la colección admins
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            admin = Admin(
                admin_id="admin_test",
                email="test@admin.com",
                hashed_password="$2b$12$hashed",
                full_name="Test Admin"
            )
            
            repo.save_admin(admin)
            
            # Verificar que se llamó insert_one con los datos correctos
            mock_collection.insert_one.assert_called_once()
            call_args = mock_collection.insert_one.call_args[0][0]
            assert call_args["admin_id"] == "admin_test"
            assert call_args["email"] == "test@admin.com"
            assert call_args["hashed_password"] == "$2b$12$hashed"
            assert call_args["full_name"] == "Test Admin"
            assert call_args["is_active"] is True
            assert call_args["is_verified"] is False


class TestAdminRepositoryFind:
    """Tests para búsqueda de administradores"""

    def test_find_by_admin_id_found(self):
        """
        TEST-REPO-003: Buscar admin existente por admin_id
        
        Given: Un admin_id que existe en la base de datos
        When: Se llama a find_by_admin_id
        Then: Se retorna la instancia de Admin correcta
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            # Mock del documento encontrado
            mock_document = {
                "admin_id": "admin_test",
                "email": "test@admin.com",
                "hashed_password": "$2b$12$hashed",
                "full_name": "Test Admin",
                "created_at": datetime.now(),
                "is_active": True,
                "is_verified": False,
                "verification_token": "123456",
                "verification_token_expires": datetime.now() + timedelta(hours=24),
                "last_login": None
            }
            mock_collection.find_one.return_value = mock_document
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            result = repo.find_by_admin_id("admin_test")
            
            # Verificar que se llamó find_one correctamente
            mock_collection.find_one.assert_called_once_with({"admin_id": "admin_test"})
            
            # Verificar que se retornó un Admin con los datos correctos
            assert result is not None
            assert result.admin_id == "admin_test"
            assert result.email == "test@admin.com"
            assert result.full_name == "Test Admin"

    def test_find_by_admin_id_not_found(self):
        """
        TEST-REPO-004: Buscar admin no existente retorna None
        
        Given: Un admin_id que no existe en la base de datos
        When: Se llama a find_by_admin_id
        Then: Se retorna None
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            # Mock de no encontrado
            mock_collection.find_one.return_value = None
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            result = repo.find_by_admin_id("nonexistent")
            
            assert result is None

    def test_find_by_email(self):
        """
        TEST-REPO-005: Buscar admin por email
        
        Given: Un email que existe en la base de datos
        When: Se llama a find_by_email
        Then: Se retorna la instancia de Admin correcta
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            mock_document = {
                "admin_id": "admin_test",
                "email": "test@admin.com",
                "hashed_password": "$2b$12$hashed",
                "full_name": "Test Admin",
                "created_at": datetime.now(),
                "is_active": True,
                "is_verified": False,
                "verification_token": None,
                "verification_token_expires": None,
                "last_login": None
            }
            mock_collection.find_one.return_value = mock_document
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            result = repo.find_by_email("test@admin.com")
            
            mock_collection.find_one.assert_called_once_with({"email": "test@admin.com"})
            assert result is not None
            assert result.email == "test@admin.com"

    def test_find_by_email_not_found(self):
        """
        TEST-REPO-005B: Buscar admin por email no existente retorna None
        
        Given: Un email que no existe en la base de datos
        When: Se llama a find_by_email
        Then: Se retorna None
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            # Mock de no encontrado
            mock_collection.find_one.return_value = None
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            result = repo.find_by_email("nonexistent@admin.com")
            
            assert result is None

    def test_find_by_verification_token(self):
        """
        TEST-REPO-006: Buscar admin por token de verificación
        
        Given: Un token de verificación que existe
        When: Se llama a find_by_verification_token
        Then: Se retorna la instancia de Admin correcta
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            mock_document = {
                "admin_id": "admin_test",
                "email": "test@admin.com",
                "hashed_password": "$2b$12$hashed",
                "full_name": "Test Admin",
                "created_at": datetime.now(),
                "is_active": True,
                "is_verified": False,
                "verification_token": "123456",
                "verification_token_expires": datetime.now() + timedelta(hours=24),
                "last_login": None
            }
            mock_collection.find_one.return_value = mock_document
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            result = repo.find_by_verification_token("123456")
            
            mock_collection.find_one.assert_called_once_with({"verification_token": "123456"})
            assert result is not None
            assert result.verification_token == "123456"

    def test_find_by_verification_token_not_found(self):
        """
        TEST-REPO-006B: Buscar admin por token no existente retorna None
        
        Given: Un token de verificación que no existe
        When: Se llama a find_by_verification_token
        Then: Se retorna None
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            # Mock de no encontrado
            mock_collection.find_one.return_value = None
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            result = repo.find_by_verification_token("nonexistent_token")
            
            assert result is None


class TestAdminRepositoryExistence:
    """Tests para verificación de existencia"""

    def test_admin_exists_true(self):
        """
        TEST-REPO-007: Verificar existencia de admin_id (existe)
        
        Given: Un admin_id que existe en la base de datos
        When: Se llama a admin_exists
        Then: Se retorna True
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            mock_collection.count_documents.return_value = 1
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            result = repo.admin_exists("admin_test")
            
            mock_collection.count_documents.assert_called_once_with({"admin_id": "admin_test"})
            assert result is True

    def test_admin_exists_false(self):
        """
        TEST-REPO-008: Verificar existencia de admin_id (no existe)
        
        Given: Un admin_id que no existe en la base de datos
        When: Se llama a admin_exists
        Then: Se retorna False
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            mock_collection.count_documents.return_value = 0
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            result = repo.admin_exists("nonexistent")
            
            assert result is False

    def test_email_exists(self):
        """
        TEST-REPO-009: Verificar existencia de email
        
        Given: Un email que existe en la base de datos
        When: Se llama a email_exists
        Then: Se retorna True
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            mock_collection.count_documents.return_value = 1
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            result = repo.email_exists("test@admin.com")
            
            mock_collection.count_documents.assert_called_once_with({"email": "test@admin.com"})
            assert result is True


class TestAdminRepositoryUpdate:
    """Tests para actualización de administradores"""

    def test_update_admin(self):
        """
        TEST-REPO-010: Actualizar datos de admin
        
        Given: Una instancia de Admin con datos modificados
        When: Se llama a update_admin
        Then: Los datos se actualizan en MongoDB
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            admin = Admin(
                admin_id="admin_test",
                email="updated@admin.com",
                hashed_password="$2b$12$newhash",
                full_name="Updated Admin",
                is_verified=True
            )
            
            repo.update_admin(admin)
            
            # Verificar que se llamó update_one correctamente
            mock_collection.update_one.assert_called_once()
            call_args = mock_collection.update_one.call_args[0]
            assert call_args[0] == {"admin_id": "admin_test"}
            assert "$set" in call_args[1]
            assert call_args[1]["$set"]["email"] == "updated@admin.com"
            assert call_args[1]["$set"]["is_verified"] is True

    def test_update_last_login(self):
        """
        TEST-REPO-011: Actualizar timestamp de último login
        
        Given: Un admin_id existente
        When: Se llama a update_last_login
        Then: El campo last_login se actualiza con la fecha actual
        """
        with patch('infrastructure.admin_repository.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.admins = mock_collection
            
            repo = AdminRepository(
                connection_string="mongodb://localhost:27017",
                database_name="test_db"
            )
            
            repo.update_last_login("admin_test")
            
            # Verificar que se llamó update_one
            mock_collection.update_one.assert_called_once()
            call_args = mock_collection.update_one.call_args[0]
            assert call_args[0] == {"admin_id": "admin_test"}
            assert "$set" in call_args[1]
            assert "last_login" in call_args[1]["$set"]
