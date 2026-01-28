"""
Admin Authentication Routes - Endpoints para autenticación de administradores

Estos endpoints manejan:
- Registro de administradores
- Login de administradores
- Verificación de email de administradores
- Obtener datos del administrador actual

Arquitectura: Clean Architecture con dependency injection
Metodología: TDD - Fase GREEN
"""
from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# DTOs para autenticación de administradores
class RegisterAdminRequest(BaseModel):
    """DTO para registro de administrador"""
    admin_id: str = Field(..., min_length=3, description="Admin ID (username)")
    email: EmailStr = Field(..., description="Admin email")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    full_name: str = Field(..., min_length=2, description="Full name")


class LoginAdminRequest(BaseModel):
    """DTO para login de administrador"""
    admin_id: str = Field(..., description="Admin ID")
    password: str = Field(..., description="Password")


class VerifyEmailRequest(BaseModel):
    """DTO para verificación de email"""
    token: str = Field(..., description="Verification token")


# Router para autenticación de administradores
admin_auth_router = APIRouter(prefix="/api/v1/admin/auth", tags=["Admin Authentication"])

# Variables globales para factories (dependency injection)
_admin_repository_factory = None
_password_service_factory = None
_jwt_service_factory = None
_email_service_factory = None
_register_admin_use_case_factory = None
_login_admin_use_case_factory = None
_verify_admin_email_use_case_factory = None
_get_current_admin_use_case_factory = None


def configure_admin_auth_dependencies(
    admin_repository_factory,
    password_service_factory,
    jwt_service_factory,
    email_service_factory,
    register_admin_use_case_factory,
    login_admin_use_case_factory,
    verify_admin_email_use_case_factory,
    get_current_admin_use_case_factory
):
    """
    Configura las factories de dependencias para autenticación de admins
    
    Esta función permite inyectar las dependencias necesarias desde main.py,
    facilitando el testing y siguiendo el principio de inversión de dependencias (SOLID-D)
    """
    global _admin_repository_factory, _password_service_factory, _jwt_service_factory
    global _email_service_factory, _register_admin_use_case_factory, _login_admin_use_case_factory
    global _verify_admin_email_use_case_factory, _get_current_admin_use_case_factory
    
    _admin_repository_factory = admin_repository_factory
    _password_service_factory = password_service_factory
    _jwt_service_factory = jwt_service_factory
    _email_service_factory = email_service_factory
    _register_admin_use_case_factory = register_admin_use_case_factory
    _login_admin_use_case_factory = login_admin_use_case_factory
    _verify_admin_email_use_case_factory = verify_admin_email_use_case_factory
    _get_current_admin_use_case_factory = get_current_admin_use_case_factory


def get_current_admin_from_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Dependency para obtener el admin actual del token JWT
    
    Args:
        authorization: Header Authorization con Bearer token
        
    Returns:
        admin_id del administrador autenticado
        
    Raises:
        HTTPException 401: Si el token es inválido o no está presente
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    jwt_service = _jwt_service_factory()
    payload = jwt_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    admin_id = payload.get("sub")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el token es de tipo admin
    token_type = payload.get("type")
    if token_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires admin privileges",
        )
    
    return admin_id


@admin_auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_admin(request: RegisterAdminRequest):
    """
    Registra un nuevo administrador en el sistema
    
    Args:
        request: Datos del administrador (admin_id, email, password, full_name)
        
    Returns:
        {
            "success": true,
            "message": "Admin registered successfully. Please check your email to verify your account.",
            "admin_id": "admin_john"
        }
        
    Raises:
        400: Si admin_id o email ya existen
        500: Error interno del servidor
    """
    try:
        register_use_case = _register_admin_use_case_factory()
        result = await register_use_case.execute(
            admin_id=request.admin_id,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering admin: {str(e)}"
        )


@admin_auth_router.post("/login")
async def login_admin(request: LoginAdminRequest):
    """
    Autentica un administrador y devuelve un token JWT
    
    Args:
        request: Credenciales del admin (admin_id, password)
        
    Returns:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "admin_id": "admin_john",
            "email": "john@admin.com",
            "full_name": "John Admin",
            "is_verified": true
        }
        
    Raises:
        401: Credenciales inválidas, cuenta inactiva o email no verificado
        500: Error interno del servidor
    """
    try:
        login_use_case = _login_admin_use_case_factory()
        result = await login_use_case.execute(
            admin_id=request.admin_id,
            password=request.password
        )
        return result
    except ValueError as e:
        error_msg = str(e).lower()
        
        # Si el error es de email no verificado, retornar 403
        if "verificar" in error_msg or "verify" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        
        # Otros errores de validación son 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )


@admin_auth_router.post("/verify-email")
async def verify_admin_email(request: VerifyEmailRequest):
    """
    Verifica el email de un administrador usando el token enviado por correo
    
    Args:
        request: Token de verificación (6 dígitos)
        
    Returns:
        {
            "success": true,
            "message": "Email verified successfully",
            "admin_id": "admin_john"
        }
        
    Raises:
        400: Token inválido o expirado
        500: Error interno del servidor
    """
    try:
        verify_use_case = _verify_admin_email_use_case_factory()
        result = await verify_use_case.execute(token=request.token)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying email: {str(e)}"
        )


@admin_auth_router.get("/me")
async def get_current_admin(admin_id: str = Depends(get_current_admin_from_token)):
    """
    Obtiene los datos del administrador actual (autenticado)
    
    Requiere token JWT válido con type="admin" en el header Authorization
    
    Args:
        admin_id: Admin ID extraído del token JWT (dependency)
        
    Returns:
        {
            "admin_id": "admin_john",
            "email": "john@admin.com",
            "full_name": "John Admin",
            "is_verified": true,
            "is_active": true,
            "created_at": "2026-01-19T10:30:00Z"
        }
        
    Raises:
        401: Token inválido, expirado o no presente
        403: Token no es de tipo admin
        404: Administrador no encontrado
        500: Error interno del servidor
    """
    try:
        get_admin_use_case = _get_current_admin_use_case_factory()
        result = await get_admin_use_case.execute(admin_id=admin_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting admin data: {str(e)}"
        )
