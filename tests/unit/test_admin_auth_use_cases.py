"""
Tests Unitarios para Admin Auth Use Cases
Siguiendo metodología TDD (Test-Driven Development)

Cumplimiento SOLID en tests:
- Single Responsibility: Cada test verifica un único comportamiento
- Open/Closed: Tests extensibles para nuevos casos de uso
- Dependency Inversion: Tests usan mocks para no depender de infraestructura real

Coverage objetivo: >70%
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

# Agregar el directorio services al path
services_path = Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service" / "src"
sys.path.insert(0, str(services_path))

from domain.models import Admin
from application.admin_auth_use_cases import (
    RegisterAdminUseCase,
    LoginAdminUseCase,
    VerifyAdminEmailUseCase
)


class TestRegisterAdminUseCase:
    """Tests para RegisterAdminUseCase"""
    
    @pytest.mark.asyncio
    async def test_register_admin_success(self):
        """
        TEST-USECASE-001: Registrar admin exitosamente
        
        Given: Datos válidos de un nuevo admin
        When: Se ejecuta RegisterAdminUseCase
        Then: Se crea el admin, se envía email y retorna success
        """
        # Mocks
        mock_repo = Mock()
        mock_repo.admin_exists = AsyncMock(return_value=False)
        mock_repo.email_exists = AsyncMock(return_value=False)
        mock_repo.save_admin = AsyncMock()
        
        mock_password_service = Mock()
        mock_password_service.hash_password = Mock(return_value="$2b$12$hashed")
        
        mock_email_service = Mock()
        mock_email_service.send_verification_email = AsyncMock()
        
        # Use case
        use_case = RegisterAdminUseCase(
            admin_repository=mock_repo,
            password_service=mock_password_service,
            email_service=mock_email_service,
            base_url="http://localhost:3001"
        )
        
        # Execute
        with patch('application.admin_auth_use_cases.TokenGenerator.generate_verification_token', return_value="123456"):
            result = await use_case.execute(
                admin_id="admin_john",
                email="john@admin.com",
                password="password123",
                full_name="John Admin"
            )
        
        # Assertions
        assert result["success"] is True
        assert result["admin_id"] == "admin_john"
        assert "registered successfully" in result["message"].lower()
        
        # Verificar llamadas
        mock_repo.admin_exists.assert_called_once_with("admin_john")
        mock_repo.email_exists.assert_called_once_with("john@admin.com")
        mock_password_service.hash_password.assert_called_once_with("password123")
        mock_repo.save_admin.assert_called_once()
        mock_email_service.send_verification_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_admin_duplicate_admin_id(self):
        """
        TEST-USECASE-002: Error al registrar admin con admin_id duplicado
        
        Given: Un admin_id que ya existe
        When: Se ejecuta RegisterAdminUseCase
        Then: Lanza ValueError("Admin ID already exists")
        """
        mock_repo = Mock()
        mock_repo.admin_exists = AsyncMock(return_value=True)
        
        use_case = RegisterAdminUseCase(
            admin_repository=mock_repo,
            password_service=Mock(),
            email_service=Mock(),
            base_url="http://localhost:3001"
        )
        
        with pytest.raises(ValueError, match="Admin ID already exists"):
            await use_case.execute(
                admin_id="admin_existing",
                email="new@admin.com",
                password="password123",
                full_name="New Admin"
            )
    
    @pytest.mark.asyncio
    async def test_register_admin_duplicate_email(self):
        """
        TEST-USECASE-003: Error al registrar admin con email duplicado
        
        Given: Un email que ya está registrado
        When: Se ejecuta RegisterAdminUseCase
        Then: Lanza ValueError("Email already registered")
        """
        mock_repo = Mock()
        mock_repo.admin_exists = AsyncMock(return_value=False)
        mock_repo.email_exists = AsyncMock(return_value=True)
        
        use_case = RegisterAdminUseCase(
            admin_repository=mock_repo,
            password_service=Mock(),
            email_service=Mock(),
            base_url="http://localhost:3001"
        )
        
        with pytest.raises(ValueError, match="Email already registered"):
            await use_case.execute(
                admin_id="admin_new",
                email="existing@admin.com",
                password="password123",
                full_name="New Admin"
            )
    
    @pytest.mark.asyncio
    async def test_register_admin_password_hashing(self):
        """
        TEST-USECASE-004: Verificar que la contraseña se hashea correctamente
        
        Given: Una contraseña en texto plano
        When: Se registra un admin
        Then: Se llama a hash_password y se guarda el hash
        """
        mock_repo = Mock()
        mock_repo.admin_exists = AsyncMock(return_value=False)
        mock_repo.email_exists = AsyncMock(return_value=False)
        mock_repo.save_admin = AsyncMock()
        
        mock_password_service = Mock()
        mock_password_service.hash_password = Mock(return_value="$2b$12$hashed_password")
        
        mock_email_service = Mock()
        mock_email_service.send_verification_email = AsyncMock()
        
        use_case = RegisterAdminUseCase(
            admin_repository=mock_repo,
            password_service=mock_password_service,
            email_service=mock_email_service,
            base_url="http://localhost:3001"
        )
        
        with patch('application.admin_auth_use_cases.TokenGenerator.generate_verification_token', return_value="123456"):
            await use_case.execute(
                admin_id="admin_test",
                email="test@admin.com",
                password="plaintext_password",
                full_name="Test Admin"
            )
        
        # Verificar que se hasheó la contraseña
        mock_password_service.hash_password.assert_called_once_with("plaintext_password")
        
        # Verificar que el admin guardado tiene el hash
        saved_admin = mock_repo.save_admin.call_args[0][0]
        assert saved_admin.hashed_password == "$2b$12$hashed_password"


class TestLoginAdminUseCase:
    """Tests para LoginAdminUseCase"""
    
    @pytest.mark.asyncio
    async def test_login_admin_success(self):
        """
        TEST-USECASE-005: Login exitoso de admin
        
        Given: Credenciales válidas de un admin verificado y activo
        When: Se ejecuta LoginAdminUseCase
        Then: Genera token JWT y actualiza last_login
        """
        # Admin mock
        admin = Admin(
            admin_id="admin_john",
            email="john@admin.com",
            hashed_password="$2b$12$hashed",
            full_name="John Admin",
            is_active=True,
            is_verified=True
        )
        
        # Mocks
        mock_repo = Mock()
        mock_repo.find_by_admin_id = AsyncMock(return_value=admin)
        mock_repo.update_last_login = AsyncMock()
        
        mock_password_service = Mock()
        mock_password_service.verify_password = Mock(return_value=True)
        
        mock_jwt_service = Mock()
        mock_jwt_service.create_access_token = Mock(return_value="jwt_token_123")
        
        # Use case
        use_case = LoginAdminUseCase(
            admin_repository=mock_repo,
            password_service=mock_password_service,
            jwt_service=mock_jwt_service
        )
        
        # Execute
        result = await use_case.execute(
            admin_id="admin_john",
            password="password123"
        )
        
        # Assertions
        assert result["access_token"] == "jwt_token_123"
        assert result["token_type"] == "bearer"
        assert result["admin_id"] == "admin_john"
        assert result["email"] == "john@admin.com"
        assert result["full_name"] == "John Admin"
        assert result["is_verified"] is True
        
        # Verificar llamadas
        mock_repo.find_by_admin_id.assert_called_once_with("admin_john")
        mock_password_service.verify_password.assert_called_once_with("password123", "$2b$12$hashed")
        mock_jwt_service.create_access_token.assert_called_once()
        mock_repo.update_last_login.assert_called_once_with("admin_john")
    
    @pytest.mark.asyncio
    async def test_login_admin_not_found(self):
        """
        TEST-USECASE-006: Error al hacer login con admin_id inexistente
        
        Given: Un admin_id que no existe
        When: Se ejecuta LoginAdminUseCase
        Then: Lanza ValueError("Invalid credentials")
        """
        mock_repo = Mock()
        mock_repo.find_by_admin_id = AsyncMock(return_value=None)
        
        use_case = LoginAdminUseCase(
            admin_repository=mock_repo,
            password_service=Mock(),
            jwt_service=Mock()
        )
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            await use_case.execute(
                admin_id="admin_nonexistent",
                password="password123"
            )
    
    @pytest.mark.asyncio
    async def test_login_admin_wrong_password(self):
        """
        TEST-USECASE-007: Error al hacer login con contraseña incorrecta
        
        Given: Contraseña incorrecta
        When: Se ejecuta LoginAdminUseCase
        Then: Lanza ValueError("Invalid credentials")
        """
        admin = Admin(
            admin_id="admin_john",
            email="john@admin.com",
            hashed_password="$2b$12$hashed",
            full_name="John Admin"
        )
        
        mock_repo = Mock()
        mock_repo.find_by_admin_id = AsyncMock(return_value=admin)
        
        mock_password_service = Mock()
        mock_password_service.verify_password = Mock(return_value=False)
        
        use_case = LoginAdminUseCase(
            admin_repository=mock_repo,
            password_service=mock_password_service,
            jwt_service=Mock()
        )
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            await use_case.execute(
                admin_id="admin_john",
                password="wrong_password"
            )
    
    @pytest.mark.asyncio
    async def test_login_admin_inactive_account(self):
        """
        TEST-USECASE-008: Error al hacer login con cuenta inactiva
        
        Given: Admin con is_active=False
        When: Se ejecuta LoginAdminUseCase
        Then: Lanza ValueError("Admin account is inactive")
        """
        admin = Admin(
            admin_id="admin_john",
            email="john@admin.com",
            hashed_password="$2b$12$hashed",
            full_name="John Admin",
            is_active=False
        )
        
        mock_repo = Mock()
        mock_repo.find_by_admin_id = AsyncMock(return_value=admin)
        
        mock_password_service = Mock()
        mock_password_service.verify_password = Mock(return_value=True)
        
        use_case = LoginAdminUseCase(
            admin_repository=mock_repo,
            password_service=mock_password_service,
            jwt_service=Mock()
        )
        
        with pytest.raises(ValueError, match="Admin account is inactive"):
            await use_case.execute(
                admin_id="admin_john",
                password="password123"
            )
    
    @pytest.mark.asyncio
    async def test_login_admin_not_verified(self):
        """
        TEST-USECASE-009: Error al hacer login sin verificar email
        
        Given: Admin con is_verified=False
        When: Se ejecuta LoginAdminUseCase
        Then: Lanza ValueError con mensaje de verificación
        """
        admin = Admin(
            admin_id="admin_john",
            email="john@admin.com",
            hashed_password="$2b$12$hashed",
            full_name="John Admin",
            is_active=True,
            is_verified=False
        )
        
        mock_repo = Mock()
        mock_repo.find_by_admin_id = AsyncMock(return_value=admin)
        
        mock_password_service = Mock()
        mock_password_service.verify_password = Mock(return_value=True)
        
        use_case = LoginAdminUseCase(
            admin_repository=mock_repo,
            password_service=mock_password_service,
            jwt_service=Mock()
        )
        
        with pytest.raises(ValueError, match="verificar tu correo"):
            await use_case.execute(
                admin_id="admin_john",
                password="password123"
            )


class TestVerifyAdminEmailUseCase:
    """Tests para VerifyAdminEmailUseCase"""
    
    @pytest.mark.asyncio
    async def test_verify_email_success(self):
        """
        TEST-USECASE-010: Verificación de email exitosa
        
        Given: Un token de verificación válido y no expirado
        When: Se ejecuta VerifyAdminEmailUseCase
        Then: Marca is_verified=True y limpia el token
        """
        admin = Admin(
            admin_id="admin_john",
            email="john@admin.com",
            hashed_password="$2b$12$hashed",
            full_name="John Admin",
            is_verified=False,
            verification_token="123456",
            verification_token_expires=datetime.now() + timedelta(hours=1)
        )
        
        mock_repo = Mock()
        mock_repo.find_by_verification_token = AsyncMock(return_value=admin)
        mock_repo.update_admin = AsyncMock()
        
        mock_email_service = Mock()
        mock_email_service.send_welcome_email = AsyncMock()
        
        use_case = VerifyAdminEmailUseCase(
            admin_repository=mock_repo,
            email_service=mock_email_service
        )
        
        result = await use_case.execute(token="123456")
        
        # Assertions
        assert result["success"] is True
        assert result["admin_id"] == "admin_john"
        assert "verified successfully" in result["message"].lower()
        
        # Verificar que se actualizó el admin
        updated_admin = mock_repo.update_admin.call_args[0][0]
        assert updated_admin.is_verified is True
        assert updated_admin.verification_token is None
        assert updated_admin.verification_token_expires is None
        
        # Verificar email de bienvenida
        mock_email_service.send_welcome_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self):
        """
        TEST-USECASE-011: Error con token inválido
        
        Given: Un token que no existe en la base de datos
        When: Se ejecuta VerifyAdminEmailUseCase
        Then: Lanza ValueError("Invalid verification token")
        """
        mock_repo = Mock()
        mock_repo.find_by_verification_token = AsyncMock(return_value=None)
        
        use_case = VerifyAdminEmailUseCase(
            admin_repository=mock_repo,
            email_service=Mock()
        )
        
        with pytest.raises(ValueError, match="Invalid verification token"):
            await use_case.execute(token="invalid_token")
    
    @pytest.mark.asyncio
    async def test_verify_email_expired_token(self):
        """
        TEST-USECASE-012: Error con token expirado
        
        Given: Un token que ya expiró (>24 horas)
        When: Se ejecuta VerifyAdminEmailUseCase
        Then: Lanza ValueError("Verification token has expired")
        """
        admin = Admin(
            admin_id="admin_john",
            email="john@admin.com",
            hashed_password="$2b$12$hashed",
            full_name="John Admin",
            is_verified=False,
            verification_token="123456",
            verification_token_expires=datetime.now() - timedelta(hours=1)  # Expirado
        )
        
        mock_repo = Mock()
        mock_repo.find_by_verification_token = AsyncMock(return_value=admin)
        
        use_case = VerifyAdminEmailUseCase(
            admin_repository=mock_repo,
            email_service=Mock()
        )
        
        with pytest.raises(ValueError, match="Verification token has expired"):
            await use_case.execute(token="123456")
    
    @pytest.mark.asyncio
    async def test_verify_email_already_verified(self):
        """
        TEST-USECASE-013: Admin ya verificado puede verificar de nuevo (idempotente)
        
        Given: Un admin que ya tiene is_verified=True
        When: Se ejecuta VerifyAdminEmailUseCase
        Then: Retorna success sin error
        """
        admin = Admin(
            admin_id="admin_john",
            email="john@admin.com",
            hashed_password="$2b$12$hashed",
            full_name="John Admin",
            is_verified=True,  # Ya verificado
            verification_token="123456",
            verification_token_expires=datetime.now() + timedelta(hours=1)
        )
        
        mock_repo = Mock()
        mock_repo.find_by_verification_token = AsyncMock(return_value=admin)
        mock_repo.update_admin = AsyncMock()
        
        mock_email_service = Mock()
        mock_email_service.send_welcome_email = AsyncMock()
        
        use_case = VerifyAdminEmailUseCase(
            admin_repository=mock_repo,
            email_service=mock_email_service
        )
        
        result = await use_case.execute(token="123456")
        
        assert result["success"] is True
        assert result["admin_id"] == "admin_john"
    
    @pytest.mark.asyncio
    async def test_verify_email_sends_welcome_email(self):
        """
        TEST-USECASE-014: Verificar que se envía email de bienvenida
        
        Given: Verificación exitosa
        When: Se ejecuta VerifyAdminEmailUseCase
        Then: Se llama a send_welcome_email con los datos correctos
        """
        admin = Admin(
            admin_id="admin_john",
            email="john@admin.com",
            hashed_password="$2b$12$hashed",
            full_name="John Admin",
            is_verified=False,
            verification_token="123456",
            verification_token_expires=datetime.now() + timedelta(hours=1)
        )
        
        mock_repo = Mock()
        mock_repo.find_by_verification_token = AsyncMock(return_value=admin)
        mock_repo.update_admin = AsyncMock()
        
        mock_email_service = Mock()
        mock_email_service.send_welcome_email = AsyncMock()
        
        use_case = VerifyAdminEmailUseCase(
            admin_repository=mock_repo,
            email_service=mock_email_service
        )
        
        await use_case.execute(token="123456")
        
        # Verificar que se envió el email de bienvenida
        mock_email_service.send_welcome_email.assert_called_once_with(
            to_email="john@admin.com",
            admin_name="John Admin"
        )
