"""
Authentication Routes - Endpoints para registro, login y verificación
"""
from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# DTOs para autenticación
class RegisterRequest(BaseModel):
    """DTO para registro de usuario"""
    user_id: str = Field(..., min_length=3, description="User ID (username)")
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    full_name: str = Field(..., min_length=2, description="Full name")


class LoginRequest(BaseModel):
    """DTO para login"""
    user_id: str = Field(..., description="User ID")
    password: str = Field(..., description="Password")


class VerifyEmailRequest(BaseModel):
    """DTO para verificación de email"""
    token: str = Field(..., description="Verification token")


# Router para autenticación
auth_router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Variables globales para factories
_user_repository_factory = None
_password_service_factory = None
_jwt_service_factory = None
_email_service_factory = None
_register_use_case_factory = None
_login_use_case_factory = None
_verify_email_use_case_factory = None
_get_current_user_use_case_factory = None


def configure_auth_dependencies(
    user_repository_factory,
    password_service_factory,
    jwt_service_factory,
    email_service_factory,
    register_use_case_factory,
    login_use_case_factory,
    verify_email_use_case_factory,
    get_current_user_use_case_factory
):
    """Configura las factories de dependencias de autenticación"""
    global _user_repository_factory, _password_service_factory, _jwt_service_factory
    global _email_service_factory, _register_use_case_factory, _login_use_case_factory
    global _verify_email_use_case_factory, _get_current_user_use_case_factory
    
    _user_repository_factory = user_repository_factory
    _password_service_factory = password_service_factory
    _jwt_service_factory = jwt_service_factory
    _email_service_factory = email_service_factory
    _register_use_case_factory = register_use_case_factory
    _login_use_case_factory = login_use_case_factory
    _verify_email_use_case_factory = verify_email_use_case_factory
    _get_current_user_use_case_factory = get_current_user_use_case_factory


async def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Dependency para obtener el usuario actual del token JWT
    
    Args:
        authorization: Header Authorization con Bearer token
        
    Returns:
        user_id del usuario autenticado
        
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
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Registra un nuevo usuario en el sistema
    
    Envía un correo de verificación al email proporcionado
    """
    try:
        register_use_case = _register_use_case_factory()
        result = await register_use_case.execute(
            user_id=request.user_id,
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
            detail=f"Error registering user: {str(e)}"
        )


@auth_router.post("/login")
async def login(request: LoginRequest):
    """
    Autentica un usuario y devuelve un token JWT
    """
    try:
        login_use_case = _login_use_case_factory()
        result = await login_use_case.execute(
            user_id=request.user_id,
            password=request.password
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )


@auth_router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest):
    """
    Verifica el email de un usuario usando el token enviado por correo
    """
    try:
        verify_use_case = _verify_email_use_case_factory()
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


@auth_router.get("/me")
async def get_current_user(user_id: str = Depends(get_current_user_from_token)):
    """
    Obtiene los datos del usuario actual (autenticado)
    Requiere token JWT válido
    """
    try:
        get_user_use_case = _get_current_user_use_case_factory()
        result = await get_user_use_case.execute(user_id=user_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user data: {str(e)}"
        )
