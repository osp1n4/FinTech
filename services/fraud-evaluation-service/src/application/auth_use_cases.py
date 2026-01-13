"""
Authentication Use Cases - Casos de uso para registro, login y verificación
Implementación de la lógica de negocio para autenticación

Cumple SOLID:
- Single Responsibility: Cada caso de uso tiene una responsabilidad única
- Dependency Inversion: Depende de interfaces, no de implementaciones
"""
from datetime import datetime, timedelta
from typing import Optional
from src.domain.models import User
from src.infrastructure.user_repository import UserRepository
from src.infrastructure.auth_service import (
    PasswordService,
    JWTService,
    EmailService,
    TokenGenerator
)


class RegisterUserUseCase:
    """
    Caso de uso para registrar un nuevo usuario
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        email_service: EmailService,
        base_url: str
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.email_service = email_service
        self.base_url = base_url
    
    async def execute(
        self,
        user_id: str,
        email: str,
        password: str,
        full_name: str
    ) -> dict:
        """
        Registra un nuevo usuario en el sistema
        
        Args:
            user_id: ID único del usuario
            email: Email del usuario
            password: Contraseña en texto plano
            full_name: Nombre completo
            
        Returns:
            Dict con el resultado de la operación
            
        Raises:
            ValueError: Si el usuario o email ya existen
        """
        # Verificar que el usuario no exista
        if await self.user_repository.user_exists(user_id):
            raise ValueError("User ID already exists")
        
        if await self.user_repository.email_exists(email):
            raise ValueError("Email already registered")
        
        # Hashear la contraseña
        hashed_password = self.password_service.hash_password(password)
        
        # Generar token de verificación
        verification_token = TokenGenerator.generate_verification_token()
        verification_expires = datetime.now() + timedelta(hours=24)
        
        # Crear la entidad User
        user = User(
            user_id=user_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_verified=False,
            verification_token=verification_token,
            verification_token_expires=verification_expires
        )
        
        # Guardar en la base de datos
        await self.user_repository.save_user(user)
        
        # Enviar email de verificación
        await self.email_service.send_verification_email(
            to_email=email,
            user_name=full_name,
            verification_token=verification_token,
            base_url=self.base_url
        )
        
        return {
            "success": True,
            "message": "User registered successfully. Please check your email to verify your account.",
            "user_id": user_id
        }


class LoginUserUseCase:
    """
    Caso de uso para autenticar un usuario
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        jwt_service: JWTService
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service
    
    async def execute(
        self,
        user_id: str,
        password: str
    ) -> dict:
        """
        Autentica un usuario y genera un token JWT
        
        Args:
            user_id: ID del usuario
            password: Contraseña en texto plano
            
        Returns:
            Dict con el token JWT y datos del usuario
            
        Raises:
            ValueError: Si las credenciales son inválidas
        """
        # Buscar usuario
        user = await self.user_repository.find_by_user_id(user_id)
        
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verificar contraseña
        if not self.password_service.verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise ValueError("User account is inactive")
        
        # Verificar que el usuario haya verificado su email
        if not user.is_verified:
            raise ValueError("Debes verificar tu correo electrónico antes de iniciar sesión. Revisa tu bandeja de entrada.")
        
        # Generar token JWT
        access_token = self.jwt_service.create_access_token(
            data={"sub": user.user_id, "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.user_id,
            "email": user.email,
            "full_name": user.full_name,
            "is_verified": user.is_verified
        }


class VerifyEmailUseCase:
    """
    Caso de uso para verificar el email de un usuario
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService
    ):
        self.user_repository = user_repository
        self.email_service = email_service
    
    async def execute(self, token: str) -> dict:
        """
        Verifica el email de un usuario usando el token
        
        Args:
            token: Token de verificación
            
        Returns:
            Dict con el resultado de la operación
            
        Raises:
            ValueError: Si el token es inválido o ha expirado
        """
        # Buscar usuario por token
        user = await self.user_repository.find_by_verification_token(token)
        
        if not user:
            raise ValueError("Invalid verification token")
        
        # Verificar que el token no haya expirado
        if user.verification_token_expires and user.verification_token_expires < datetime.now():
            raise ValueError("Verification token has expired")
        
        # Marcar usuario como verificado
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        
        await self.user_repository.update_user(user)
        
        # Enviar email de bienvenida
        await self.email_service.send_welcome_email(
            to_email=user.email,
            user_name=user.full_name
        )
        
        return {
            "success": True,
            "message": "Email verified successfully",
            "user_id": user.user_id
        }


class GetCurrentUserUseCase:
    """
    Caso de uso para obtener los datos del usuario actual
    """
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, user_id: str) -> dict:
        """
        Obtiene los datos del usuario actual
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con los datos del usuario
            
        Raises:
            ValueError: Si el usuario no existe
        """
        user = await self.user_repository.find_by_user_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        return {
            "user_id": user.user_id,
            "email": user.email,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
