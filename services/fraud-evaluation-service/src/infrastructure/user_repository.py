"""
User Repository - Adaptador para persistencia de usuarios en MongoDB
Implementación del patrón Repository para la entidad User
"""
from typing import Optional
from datetime import datetime
from pymongo import MongoClient
from src.domain.models import User


class UserRepository:
    """
    Repository para la entidad User
    Maneja la persistencia en MongoDB
    """
    
    def __init__(self, connection_string: str, database_name: str) -> None:
        """
        Inicializa el repository de usuarios
        
        Args:
            connection_string: URL de conexión a MongoDB
            database_name: Nombre de la base de datos
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.users = self.db.users
        
        # Crear índices para optimizar búsquedas
        self.users.create_index("user_id", unique=True)
        self.users.create_index("email", unique=True)
        self.users.create_index("verification_token")
    
    async def save_user(self, user: User) -> None:
        """
        Guarda un nuevo usuario en la base de datos
        
        Args:
            user: Entidad User a guardar
        """
        document = {
            "user_id": user.user_id,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "full_name": user.full_name,
            "created_at": user.created_at,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "verification_token": user.verification_token,
            "verification_token_expires": user.verification_token_expires,
        }
        self.users.insert_one(document)
    
    async def find_by_user_id(self, user_id: str) -> Optional[User]:
        """
        Busca un usuario por su user_id
        
        Args:
            user_id: ID del usuario
            
        Returns:
            User si existe, None en caso contrario
        """
        document = self.users.find_one({"user_id": user_id})
        if not document:
            return None
        
        return User(
            user_id=document["user_id"],
            email=document["email"],
            hashed_password=document["hashed_password"],
            full_name=document["full_name"],
            created_at=document["created_at"],
            is_active=document.get("is_active", True),
            is_verified=document.get("is_verified", False),
            verification_token=document.get("verification_token"),
            verification_token_expires=document.get("verification_token_expires"),
        )
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por su email
        
        Args:
            email: Email del usuario
            
        Returns:
            User si existe, None en caso contrario
        """
        document = self.users.find_one({"email": email})
        if not document:
            return None
        
        return User(
            user_id=document["user_id"],
            email=document["email"],
            hashed_password=document["hashed_password"],
            full_name=document["full_name"],
            created_at=document["created_at"],
            is_active=document.get("is_active", True),
            is_verified=document.get("is_verified", False),
            verification_token=document.get("verification_token"),
            verification_token_expires=document.get("verification_token_expires"),
        )
    
    async def find_by_verification_token(self, token: str) -> Optional[User]:
        """
        Busca un usuario por su token de verificación
        
        Args:
            token: Token de verificación
            
        Returns:
            User si existe, None en caso contrario
        """
        document = self.users.find_one({"verification_token": token})
        if not document:
            return None
        
        return User(
            user_id=document["user_id"],
            email=document["email"],
            hashed_password=document["hashed_password"],
            full_name=document["full_name"],
            created_at=document["created_at"],
            is_active=document.get("is_active", True),
            is_verified=document.get("is_verified", False),
            verification_token=document.get("verification_token"),
            verification_token_expires=document.get("verification_token_expires"),
        )
    
    async def update_user(self, user: User) -> None:
        """
        Actualiza un usuario existente
        
        Args:
            user: Entidad User con los datos actualizados
        """
        self.users.update_one(
            {"user_id": user.user_id},
            {"$set": {
                "email": user.email,
                "hashed_password": user.hashed_password,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "verification_token": user.verification_token,
                "verification_token_expires": user.verification_token_expires,
            }}
        )
    
    async def user_exists(self, user_id: str) -> bool:
        """
        Verifica si existe un usuario con el user_id dado
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si existe, False en caso contrario
        """
        return self.users.count_documents({"user_id": user_id}) > 0
    
    async def email_exists(self, email: str) -> bool:
        """
        Verifica si existe un usuario con el email dado
        
        Args:
            email: Email del usuario
            
        Returns:
            True si existe, False en caso contrario
        """
        return self.users.count_documents({"email": email}) > 0
