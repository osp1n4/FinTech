"""
Authentication Middleware - JWT validation

Cumple Single Responsibility: Solo maneja autenticación
"""
from fastapi import HTTPException, Header, status
from typing import Optional
import jwt
from datetime import datetime, timedelta


# Configuración JWT (en producción debe venir de variables de entorno)
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"


def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verifica el token JWT del header Authorization
    
    Args:
        authorization: Header Authorization con formato "Bearer <token>"
    
    Returns:
        dict con claims del token (user_id, role, etc.)
    
    Raises:
        HTTPException: Si el token es inválido o falta
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extraer token del header "Bearer <token>"
        scheme, token = authorization.split()
        
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Decodificar y verificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        return payload
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT con los datos proporcionados
    
    Args:
        data: Datos a incluir en el token (user_id, role, etc.)
        expires_delta: Tiempo de expiración (por defecto 30 minutos)
    
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_admin_role(token_data: dict) -> None:
    """
    Verifica que el usuario tenga rol de administrador
    
    Args:
        token_data: Claims del token JWT
    
    Raises:
        HTTPException: Si el usuario no es administrador
    """
    role = token_data.get("role")
    
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
