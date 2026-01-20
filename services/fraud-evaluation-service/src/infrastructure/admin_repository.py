"""
Admin Repository - Adaptador para persistencia de administradores en MongoDB
Implementación del patrón Repository para la entidad Admin

Cumplimiento SOLID:
- Single Responsibility: Solo maneja persistencia de Admin en MongoDB
- Open/Closed: Abierto a extensión (nuevos métodos) cerrado a modificación
- Liskov Substitution: Puede implementar IAdminRepository
- Interface Segregation: Solo métodos necesarios para Admin
- Dependency Inversion: Depende de abstracciones (pymongo) no implementaciones
"""
from typing import Optional
from datetime import datetime
from pymongo import MongoClient
from domain.models import Admin


class AdminRepository:
    """
    Repository para la entidad Admin
    Maneja la persistencia en MongoDB en colección separada 'admins'
    """
    
    def __init__(self, connection_string: str, database_name: str) -> None:
        """
        Inicializa el repository de administradores
        
        Args:
            connection_string: URL de conexión a MongoDB
            database_name: Nombre de la base de datos
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.admins = self.db.admins
        
        # Crear índices para optimizar búsquedas y garantizar unicidad
        self.admins.create_index("admin_id", unique=True)
        self.admins.create_index("email", unique=True)
        self.admins.create_index("verification_token")
    
    def save_admin(self, admin: Admin) -> None:
        """
        Guarda un nuevo administrador en la base de datos
        
        Args:
            admin: Entidad Admin a guardar
        
        Raises:
            DuplicateKeyError: Si admin_id o email ya existen
        """
        document = {
            "admin_id": admin.admin_id,
            "email": admin.email,
            "hashed_password": admin.hashed_password,
            "full_name": admin.full_name,
            "created_at": admin.created_at,
            "is_active": admin.is_active,
            "is_verified": admin.is_verified,
            "verification_token": admin.verification_token,
            "verification_token_expires": admin.verification_token_expires,
            "last_login": admin.last_login,
        }
        self.admins.insert_one(document)
    
    def find_by_admin_id(self, admin_id: str) -> Optional[Admin]:
        """
        Busca un administrador por su admin_id
        
        Args:
            admin_id: ID del administrador
            
        Returns:
            Admin si existe, None en caso contrario
        """
        document = self.admins.find_one({"admin_id": admin_id})
        if not document:
            return None
        
        return Admin(
            admin_id=document["admin_id"],
            email=document["email"],
            hashed_password=document["hashed_password"],
            full_name=document["full_name"],
            created_at=document["created_at"],
            is_active=document.get("is_active", True),
            is_verified=document.get("is_verified", False),
            verification_token=document.get("verification_token"),
            verification_token_expires=document.get("verification_token_expires"),
            last_login=document.get("last_login"),
        )
    
    def find_by_email(self, email: str) -> Optional[Admin]:
        """
        Busca un administrador por su email
        
        Args:
            email: Email del administrador
            
        Returns:
            Admin si existe, None en caso contrario
        """
        document = self.admins.find_one({"email": email})
        if not document:
            return None
        
        return Admin(
            admin_id=document["admin_id"],
            email=document["email"],
            hashed_password=document["hashed_password"],
            full_name=document["full_name"],
            created_at=document["created_at"],
            is_active=document.get("is_active", True),
            is_verified=document.get("is_verified", False),
            verification_token=document.get("verification_token"),
            verification_token_expires=document.get("verification_token_expires"),
            last_login=document.get("last_login"),
        )
    
    def find_by_verification_token(self, token: str) -> Optional[Admin]:
        """
        Busca un administrador por su token de verificación
        
        Args:
            token: Token de verificación
            
        Returns:
            Admin si existe, None en caso contrario
        """
        document = self.admins.find_one({"verification_token": token})
        if not document:
            return None
        
        return Admin(
            admin_id=document["admin_id"],
            email=document["email"],
            hashed_password=document["hashed_password"],
            full_name=document["full_name"],
            created_at=document["created_at"],
            is_active=document.get("is_active", True),
            is_verified=document.get("is_verified", False),
            verification_token=document.get("verification_token"),
            verification_token_expires=document.get("verification_token_expires"),
            last_login=document.get("last_login"),
        )
    
    def update_admin(self, admin: Admin) -> None:
        """
        Actualiza un administrador existente
        
        Args:
            admin: Entidad Admin con los datos actualizados
        """
        self.admins.update_one(
            {"admin_id": admin.admin_id},
            {"$set": {
                "email": admin.email,
                "hashed_password": admin.hashed_password,
                "full_name": admin.full_name,
                "is_active": admin.is_active,
                "is_verified": admin.is_verified,
                "verification_token": admin.verification_token,
                "verification_token_expires": admin.verification_token_expires,
                "last_login": admin.last_login,
            }}
        )
    
    def update_last_login(self, admin_id: str) -> None:
        """
        Actualiza el timestamp de último login de un administrador
        
        Args:
            admin_id: ID del administrador
        """
        self.admins.update_one(
            {"admin_id": admin_id},
            {"$set": {"last_login": datetime.now()}}
        )
    
    def admin_exists(self, admin_id: str) -> bool:
        """
        Verifica si existe un administrador con el admin_id dado
        
        Args:
            admin_id: ID del administrador
            
        Returns:
            True si existe, False en caso contrario
        """
        return self.admins.count_documents({"admin_id": admin_id}) > 0
    
    def email_exists(self, email: str) -> bool:
        """
        Verifica si existe un administrador con el email dado
        
        Args:
            email: Email del administrador
            
        Returns:
            True si existe, False en caso contrario
        """
        return self.admins.count_documents({"email": email}) > 0
