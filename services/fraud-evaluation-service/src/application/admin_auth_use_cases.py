"""
Admin Authentication Use Cases - Casos de uso para registro, login y verificación de admins
Implementación de la lógica de negocio para autenticación de administradores

Cumple SOLID:
- Single Responsibility: Cada caso de uso tiene una responsabilidad única
- Open/Closed: Abierto a extensión, cerrado a modificación
- Liskov Substitution: Casos de uso intercambiables con interface común
- Interface Segregation: Cada caso de uso solo usa métodos necesarios
- Dependency Inversion: Depende de interfaces, no de implementaciones concretas
"""
from datetime import datetime, timedelta
from typing import Optional
from domain.models import Admin
from infrastructure.admin_repository import AdminRepository
from infrastructure.auth_service import (
    PasswordService,
    JWTService,
    EmailService,
    TokenGenerator
)


class RegisterAdminUseCase:
    """
    Caso de uso para registrar un nuevo administrador
    
    Responsabilidad única: Orquestar el proceso de registro de admin
    incluyendo validaciones, hash de password y envío de email
    """
    
    def __init__(
        self,
        admin_repository: AdminRepository,
        password_service: PasswordService,
        email_service: EmailService,
        base_url: str
    ):
        """
        Inicializa el caso de uso con sus dependencias
        
        Args:
            admin_repository: Repositorio para persistencia de admins
            password_service: Servicio para hashear passwords
            email_service: Servicio para envío de emails
            base_url: URL base de la aplicación admin
        """
        self.admin_repository = admin_repository
        self.password_service = password_service
        self.email_service = email_service
        self.base_url = base_url
    
    async def execute(
        self,
        admin_id: str,
        email: str,
        password: str,
        full_name: str
    ) -> dict:
        """
        Registra un nuevo administrador en el sistema
        
        Flujo:
        1. Validar que admin_id no exista
        2. Validar que email no exista
        3. Hashear password
        4. Generar token de verificación (6 dígitos, expira en 24h)
        5. Crear entidad Admin
        6. Guardar en MongoDB (colección 'admins')
        7. Enviar email de verificación
        
        Args:
            admin_id: ID único del administrador
            email: Email del administrador
            password: Contraseña en texto plano
            full_name: Nombre completo
            
        Returns:
            Dict con el resultado de la operación:
            {
                "success": True,
                "message": "Admin registered successfully...",
                "admin_id": "admin_john"
            }
            
        Raises:
            ValueError: Si el admin_id o email ya existen
        """
        # Verificar que el admin no exista
        if await self.admin_repository.admin_exists(admin_id):
            raise ValueError("Admin ID already exists")
        
        if await self.admin_repository.email_exists(email):
            raise ValueError("Email already registered")
        
        # Hashear la contraseña
        hashed_password = self.password_service.hash_password(password)
        
        # Generar token de verificación de 6 dígitos
        verification_token = TokenGenerator.generate_verification_token()
        verification_expires = datetime.now() + timedelta(hours=24)
        
        # Crear la entidad Admin
        admin = Admin(
            admin_id=admin_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_verified=False,
            verification_token=verification_token,
            verification_token_expires=verification_expires
        )
        
        # Guardar en la base de datos (colección 'admins')
        await self.admin_repository.save_admin(admin)
        
        # Enviar email de verificación
        await self.email_service.send_verification_email(
            to_email=email,
            user_name=full_name,
            verification_token=verification_token,
            base_url=self.base_url
        )
        
        return {
            "success": True,
            "message": "Admin registered successfully. Please check your email to verify your account.",
            "admin_id": admin_id
        }


class LoginAdminUseCase:
    """
    Caso de uso para autenticar un administrador
    
    Responsabilidad única: Orquestar el proceso de login incluyendo
    validaciones, verificación de password y generación de JWT
    """
    
    def __init__(
        self,
        admin_repository: AdminRepository,
        password_service: PasswordService,
        jwt_service: JWTService
    ):
        """
        Inicializa el caso de uso con sus dependencias
        
        Args:
            admin_repository: Repositorio para buscar admins
            password_service: Servicio para verificar passwords
            jwt_service: Servicio para generar tokens JWT
        """
        self.admin_repository = admin_repository
        self.password_service = password_service
        self.jwt_service = jwt_service
    
    async def execute(
        self,
        admin_id: str,
        password: str
    ) -> dict:
        """
        Autentica un administrador y genera un token JWT
        
        Flujo:
        1. Buscar admin por admin_id
        2. Verificar password con bcrypt
        3. Validar que la cuenta esté activa (is_active=True)
        4. CRÍTICO: Validar que el email esté verificado (is_verified=True)
        5. Generar token JWT con payload: {"sub": admin_id, "email": email, "type": "admin"}
        6. Actualizar last_login en MongoDB
        7. Retornar token y datos del admin
        
        Args:
            admin_id: ID del administrador
            password: Contraseña en texto plano
            
        Returns:
            Dict con el token JWT y datos del administrador:
            {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "admin_id": "admin_john",
                "email": "john@admin.com",
                "full_name": "John Admin",
                "is_verified": True
            }
            
        Raises:
            ValueError: Si las credenciales son inválidas, cuenta inactiva o email no verificado
        """
        # Buscar administrador
        admin = await self.admin_repository.find_by_admin_id(admin_id)
        
        if not admin:
            raise ValueError("Invalid credentials")
        
        # Verificar contraseña
        if not self.password_service.verify_password(password, admin.hashed_password):
            raise ValueError("Invalid credentials")
        
        # Verificar que el administrador esté activo
        if not admin.is_active:
            raise ValueError("Admin account is inactive")
        
        # CRÍTICO: Verificar que el administrador haya verificado su email
        if not admin.is_verified:
            raise ValueError("Debes verificar tu correo electrónico antes de iniciar sesión")
        
        # Generar token JWT con tipo "admin"
        token_data = {
            "sub": admin.admin_id,
            "email": admin.email,
            "type": "admin"  # Identificador de tipo de usuario
        }
        access_token = self.jwt_service.create_access_token(token_data)
        
        # Actualizar último login
        await self.admin_repository.update_last_login(admin.admin_id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "admin_id": admin.admin_id,
            "email": admin.email,
            "full_name": admin.full_name,
            "is_verified": admin.is_verified
        }


class VerifyAdminEmailUseCase:
    """
    Caso de uso para verificar el email de un administrador
    
    Responsabilidad única: Orquestar el proceso de verificación de email
    validando el token y actualizando el estado del admin
    """
    
    def __init__(
        self,
        admin_repository: AdminRepository,
        email_service: EmailService
    ):
        """
        Inicializa el caso de uso con sus dependencias
        
        Args:
            admin_repository: Repositorio para buscar y actualizar admins
            email_service: Servicio para enviar email de bienvenida
        """
        self.admin_repository = admin_repository
        self.email_service = email_service
    
    async def execute(self, token: str) -> dict:
        """
        Verifica el email de un administrador usando el token de verificación
        
        Flujo:
        1. Buscar admin por verification_token
        2. Validar que el admin exista
        3. Verificar que el token no haya expirado (24 horas)
        4. Marcar is_verified=True
        5. Limpiar verification_token y verification_token_expires
        6. Actualizar admin en MongoDB
        7. Enviar email de bienvenida
        
        Args:
            token: Token de verificación de 6 dígitos
            
        Returns:
            Dict con el resultado de la operación:
            {
                "success": True,
                "message": "Email verified successfully",
                "admin_id": "admin_john"
            }
            
        Raises:
            ValueError: Si el token es inválido o ha expirado
        """
        # Buscar admin por token
        admin = await self.admin_repository.find_by_verification_token(token)
        
        if not admin:
            raise ValueError("Invalid verification token")
        
        # Verificar que el token no haya expirado
        if admin.verification_token_expires and admin.verification_token_expires < datetime.now():
            raise ValueError("Verification token has expired")
        
        # Marcar como verificado y limpiar token
        admin.is_verified = True
        admin.verification_token = None
        admin.verification_token_expires = None
        
        # Actualizar en la base de datos
        await self.admin_repository.update_admin(admin)
        
        # Enviar email de bienvenida
        await self.email_service.send_welcome_email(
            to_email=admin.email,
            admin_name=admin.full_name
        )
        
        return {
            "success": True,
            "message": "Email verified successfully",
            "admin_id": admin.admin_id
        }
