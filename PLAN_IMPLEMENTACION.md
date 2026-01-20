# 📋 Plan de Implementación - Sistema de Autenticación para Administradores

**Proyecto:** FinTech - Sistema de Detección de Fraude  
**Fecha:** 19 de Enero de 2026  
**Objetivo:** Implementar autenticación completa para el Admin Dashboard (http://localhost:3001/)

---

## 🎯 Visión General

Actualmente el sistema cuenta con **autenticación completa para usuarios finales** (http://localhost:3000/), pero el **Admin Dashboard** (http://localhost:3001/) **no tiene sistema de login**.

Este plan describe la **Fase 1** para implementar autenticación de administradores reutilizando la arquitectura existente, **sin implementar sistema de roles** (se mantiene la simplicidad actual).

---

## 🎯 Metodología del Plan: TDD + SOLID + Clean Code

### **Ciclo TDD Estricto en Cada Paso**

Todos los pasos de implementación siguen el ciclo **Red → Green → Refactor**:

| Fase | Acción | Commit | Push |
|------|--------|--------|------|
| 🔴 **RED** | Escribir test que falla | `RED: add failing test for [feature]` | `git push origin feature/admin-auth` |
| 🟢 **GREEN** | Implementar código mínimo | `GREEN: implement [feature]` | `git push origin feature/admin-auth` |
| ♻️ **REFACTOR** | Optimizar manteniendo tests verdes | `REFACTOR: optimize [feature] logic` | `git push origin feature/admin-auth` |

### **Objetivos de Calidad**

| Métrica | Objetivo | Herramienta |
|---------|----------|-------------|
| **Cobertura de código** | >70% | pytest --cov |
| **Tests unitarios** | 30+ tests | pytest tests/unit/ |
| **Tests de integración** | 8+ tests | pytest tests/integration/ |
| **Tests E2E** | 6+ tests | Playwright |
| **Principios SOLID** | 0 violaciones | Manual review |
| **Clean Code** | Nombres descriptivos, sin duplicación | Manual review |

### **Estructura de Tests**

```
tests/
├── unit/                    # >70% cobertura
│   ├── test_admin_model.py              # 5 tests
│   ├── test_admin_repository.py         # 11 tests
│   └── test_admin_auth_use_cases.py     # 14 tests
├── integration/
│   └── test_admin_auth_endpoints.py     # 8 tests
└── coverage/htmlcov/        # Reportes HTML

tests-e2e/
└── tests/
    └── admin-auth.spec.ts   # 6 tests E2E
```

### **Commits Esperados: ~20 commits**

Cada paso genera múltiples commits siguiendo TDD y buenas prácticas Git.

---

## 📊 Estado Actual del Sistema

### ✅ Componentes Existentes (Usuario Final)

| Componente | Ubicación | Estado |
|------------|-----------|--------|
| RegisterUserUseCase | `services/fraud-evaluation-service/src/application/auth_use_cases.py` | ✅ Implementado |
| LoginUserUseCase | `services/fraud-evaluation-service/src/application/auth_use_cases.py` | ✅ Implementado |
| VerifyEmailUseCase | `services/fraud-evaluation-service/src/application/auth_use_cases.py` | ✅ Implementado |
| User Entity | `services/fraud-evaluation-service/src/domain/models.py` | ✅ Implementado |
| UserRepository | `services/fraud-evaluation-service/src/infrastructure/user_repository.py` | ✅ Implementado |
| PasswordService | `services/fraud-evaluation-service/src/infrastructure/auth_service.py` | ✅ Implementado |
| JWTService | `services/fraud-evaluation-service/src/infrastructure/auth_service.py` | ✅ Implementado |
| EmailService | `services/fraud-evaluation-service/src/infrastructure/auth_service.py` | ✅ Implementado |
| Auth Routes (API) | `services/api-gateway/src/auth_routes.py` | ✅ Implementado |
| LoginPage (Frontend) | `frontend/user-app/src/pages/LoginPage.tsx` | ✅ Implementado |
| RegisterPage (Frontend) | `frontend/user-app/src/pages/RegisterPage.tsx` | ✅ Implementado |
| VerifyEmailPage (Frontend) | `frontend/user-app/src/pages/VerifyEmailPage.tsx` | ✅ Implementado |

### ❌ Componentes Faltantes (Administrador)

| Componente | Ubicación Propuesta | Estado |
|------------|---------------------|--------|
| Admin Entity | `services/fraud-evaluation-service/src/domain/models.py` | ❌ No existe |
| AdminRepository | `services/fraud-evaluation-service/src/infrastructure/admin_repository.py` | ❌ No existe |
| RegisterAdminUseCase | `services/fraud-evaluation-service/src/application/admin_auth_use_cases.py` | ❌ No existe |
| LoginAdminUseCase | `services/fraud-evaluation-service/src/application/admin_auth_use_cases.py` | ❌ No existe |
| VerifyAdminEmailUseCase | `services/fraud-evaluation-service/src/application/admin_auth_use_cases.py` | ❌ No existe |
| Admin Auth Routes | `services/api-gateway/src/admin_auth_routes.py` | ❌ No existe |
| LoginPage (Admin) | `frontend/admin-dashboard/src/pages/LoginPage.tsx` | ❌ No existe |
| RegisterPage (Admin) | `frontend/admin-dashboard/src/pages/RegisterPage.tsx` | ❌ No existe |
| VerifyEmailPage (Admin) | `frontend/admin-dashboard/src/pages/VerifyEmailPage.tsx` | ❌ No existe |
| ProtectedRoute (Admin) | `frontend/admin-dashboard/src/components/ProtectedRoute.tsx` | ❌ No existe |

---

## 🚀 FASE 1: Implementación de Login para Administrador

### **Duración Estimada:** 1 semana (5 días laborables)

---

## 📝 Paso 1: Definir Modelo de Dominio para Admin

### **Objetivo**
Crear la entidad `Admin` en el dominio, separada de `User`, manteniendo la misma estructura de autenticación.

### **Archivo a Modificar**
- `services/fraud-evaluation-service/src/domain/models.py`

### **Definición del Modelo Admin**

```python
@dataclass
class Admin:
    """
    Entidad de dominio para administradores del sistema
    Similar a User pero con colección MongoDB separada
    """
    admin_id: str                      # Identificador único (ej: "admin_john")
    email: str                         # Email único
    hashed_password: str               # Password hasheado con bcrypt
    full_name: str                     # Nombre completo del administrador
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True             # Cuenta activa/inactiva
    is_verified: bool = False          # Email verificado
    verification_token: Optional[str] = None
    verification_token_expires: Optional[datetime] = None
    last_login: Optional[datetime] = None
```

### **Diferencias con User**
- **Campo**: `admin_id` (en lugar de `user_id`)
- **Propósito**: Identificar claramente que es un administrador
- **Base de datos**: Colección separada `admins` en MongoDB
- **Sin roles**: Se mantiene simple, un admin es un admin

### **Validaciones Requeridas**
- `admin_id`: Mínimo 3 caracteres, solo alfanuméricos y guiones bajos
- `email`: Formato válido de email, único en la colección
- `password`: Mínimo 6 caracteres (en el caso de uso)
- `full_name`: Mínimo 2 caracteres

### **Metodología TDD**
- **Red**: Escribir test para modelo Admin antes de implementar.
  - Archivo: `tests/unit/test_admin_model.py`
  - Commit: `git commit -m "RED: add failing test for Admin entity model"`
  - Push: `git push origin feature/admin-auth`
- **Green**: Implementar modelo Admin para pasar tests.
  - Commit: `git commit -m "GREEN: implement Admin entity model"`
  - Push: `git push origin feature/admin-auth`
- **Refactor**: Optimizar modelo manteniendo tests verdes.
  - Commit: `git commit -m "REFACTOR: optimize Admin entity validations"`
  - Push: `git push origin feature/admin-auth`
- **Ciclo estricto**: Seguir Red → Green → Refactor sin saltarse pasos.
- **Después de cada paso**: Ejecutar `git push` para sincronizar con GitHub.

### **Cobertura**
- **Objetivo**: >70% en modelo Admin
- **Comando**: `pytest tests/unit/test_admin_model.py --cov=services.fraud-evaluation-service.src.domain.models --cov-report=html --cov-report=term`
- **Reporte HTML**: `htmlcov/index.html`

### **Tests Específicos**
- `test_admin_creation_valid()`: Crear Admin con datos válidos
- `test_admin_id_validation()`: Validar formato de admin_id
- `test_email_format_validation()`: Validar formato de email
- `test_admin_defaults()`: Verificar valores por defecto (is_active, is_verified)
- `test_admin_serialization()`: Verificar conversión a dict para MongoDB

### **Tests Unitarios**
- **Ruta**: `tests/unit/test_admin_model.py`
- **Cobertura**: >70% en lógica del modelo
- **Total de tests**: Mínimo 5 tests

### **Código Limpio y Principios SOLID**
- **0 violaciones a principios SOLID**:
  - **S (Single Responsibility)**: Admin solo representa un administrador del sistema, sin lógica de negocio adicional.
  - **O (Open/Closed)**: Entidad abierta a extensión (herencia si fuera necesario) pero cerrada a modificación.
  - **L (Liskov Substitution)**: Admin puede ser tratado como cualquier otra entidad de dominio sin cambios.
  - **I (Interface Segregation)**: Admin no implementa interfaces innecesarias, solo las propias de una entidad.
  - **D (Dependency Inversion)**: Admin no depende de implementaciones concretas, solo de tipos básicos de Python.
- **Clean Code**: 
  - Nombres descriptivos (`admin_id`, `is_verified`, `verification_token_expires`)
  - Sin condicionales anidados
  - Validaciones explícitas y claras
  - Documentación clara en docstrings

### **Entregables**
- ✅ **Característica funcional**: Entidad `Admin` en `models.py` con todos los campos requeridos
- ✅ **Tests unitarios**: `tests/unit/test_admin_model.py` con mínimo 5 tests
- ✅ **Reporte de cobertura**: >70% en modelo Admin
- ✅ **Commits TDD**: 3 commits (RED, GREEN, REFACTOR) sincronizados con GitHub

---

## 📝 Paso 2: Crear AdminRepository

### **Objetivo**
Implementar repositorio para persistir administradores en MongoDB, usando colección separada.

### **Archivo a Crear**
- `services/fraud-evaluation-service/src/infrastructure/admin_repository.py`

### **Responsabilidades del AdminRepository**

1. **Guardar nuevo admin** (`save_admin`)
2. **Buscar admin por admin_id** (`find_by_admin_id`)
3. **Buscar admin por email** (`find_by_email`)
4. **Verificar existencia de admin_id** (`admin_exists`)
5. **Verificar existencia de email** (`email_exists`)
6. **Buscar por token de verificación** (`find_by_verification_token`)
7. **Actualizar admin** (`update_admin`)
8. **Actualizar último login** (`update_last_login`)

### **Colección MongoDB**
- **Nombre**: `admins` (separada de `users`)
- **Base de datos**: Misma base de datos (`fraud_detection`)

### **Índices Requeridos**
```python
# Índices únicos para performance y constraints
self.admins.create_index("admin_id", unique=True)
self.admins.create_index("email", unique=True)
self.admins.create_index("verification_token")  # Para búsquedas rápidas
```

### **Servicios Reutilizados**
- **PasswordService**: Ya existe, se reutiliza para hashear passwords
- **JWTService**: Ya existe, se reutiliza para generar tokens
- **EmailService**: Ya existe, se reutiliza para enviar correos
- **TokenGenerator**: Ya existe, se reutiliza para códigos de verificación

### **Metodología TDD**
- **Red**: Escribir tests para AdminRepository antes de implementar.
  - Archivo: `tests/unit/test_admin_repository.py`
  - Commit: `git commit -m "RED: add failing tests for AdminRepository"`
  - Push: `git push origin feature/admin-auth`
- **Green**: Implementar AdminRepository para pasar tests.
  - Commit: `git commit -m "GREEN: implement AdminRepository with MongoDB"`
  - Push: `git push origin feature/admin-auth`
- **Refactor**: Optimizar queries y manejo de excepciones.
  - Commit: `git commit -m "REFACTOR: optimize AdminRepository queries and error handling"`
  - Push: `git push origin feature/admin-auth`
- **Ciclo estricto**: Seguir Red → Green → Refactor sin saltarse pasos.
- **Después de cada paso**: Ejecutar `git push` para sincronizar con GitHub.

### **Cobertura**
- **Objetivo**: >70% en AdminRepository
- **Comando**: `pytest tests/unit/test_admin_repository.py --cov=services.fraud-evaluation-service.src.infrastructure.admin_repository --cov-report=html --cov-report=term`
- **Reporte HTML**: `htmlcov/index.html`

### **Tests Específicos**
- `test_save_admin()`: Guardar admin en MongoDB
- `test_find_by_admin_id_found()`: Buscar admin existente
- `test_find_by_admin_id_not_found()`: Buscar admin no existente retorna None
- `test_find_by_email()`: Buscar por email
- `test_admin_exists()`: Verificar existencia de admin_id
- `test_email_exists()`: Verificar existencia de email
- `test_find_by_verification_token()`: Buscar por token de verificación
- `test_update_admin()`: Actualizar datos de admin
- `test_update_last_login()`: Actualizar timestamp de último login
- `test_unique_constraint_admin_id()`: Violación de constraint único en admin_id
- `test_unique_constraint_email()`: Violación de constraint único en email

### **Tests Unitarios**
- **Ruta**: `tests/unit/test_admin_repository.py`
- **Cobertura**: >70% en lógica del repositorio
- **Total de tests**: Mínimo 11 tests

### **Código Limpio y Principios SOLID**
- **0 violaciones a principios SOLID**:
  - **S (Single Responsibility)**: AdminRepository solo se encarga de persistencia de Admin, no de lógica de negocio.
  - **O (Open/Closed)**: Abierto a extensión (agregar más métodos) pero cerrado a modificación.
  - **L (Liskov Substitution)**: Puede implementar IAdminRepository y ser sustituible por otras implementaciones.
  - **I (Interface Segregation)**: Solo métodos necesarios para persistencia de Admin, no métodos genéricos innecesarios.
  - **D (Dependency Inversion)**: Depende de abstracciones (pymongo) no de implementaciones concretas de MongoDB.
- **Clean Code**: 
  - Métodos con nombres descriptivos (`find_by_admin_id`, `admin_exists`)
  - Manejo explícito de errores (try/except con mensajes claros)
  - Sin lógica de negocio en el repositorio
  - Queries optimizadas con índices

### **Entregables**
- ✅ **Característica funcional**: AdminRepository con 8 métodos CRUD completos
- ✅ **Tests unitarios**: `tests/unit/test_admin_repository.py` con mínimo 11 tests
- ✅ **Reporte de cobertura**: >70% en AdminRepository
- ✅ **Commits TDD**: 3 commits (RED, GREEN, REFACTOR) sincronizados con GitHub

---

## 📝 Paso 3: Crear Casos de Uso para Admin

### **Objetivo**
Implementar la lógica de negocio para registro, login y verificación de administradores.

### **Archivo a Crear**
- `services/fraud-evaluation-service/src/application/admin_auth_use_cases.py`

### **3.1 RegisterAdminUseCase**

**Flujo:**
1. Validar que `admin_id` no exista
2. Validar que `email` no exista
3. Hashear password con bcrypt (usando `PasswordService`)
4. Generar token de verificación de 6 dígitos (usando `TokenGenerator`)
5. Establecer expiración del token (24 horas)
6. Crear entidad `Admin`
7. Guardar en MongoDB (colección `admins`)
8. Enviar email de verificación con código

**Input:**
- `admin_id`: str
- `email`: str
- `password`: str
- `full_name`: str

**Output:**
```json
{
  "success": true,
  "message": "Admin registered successfully. Please check your email to verify your account.",
  "admin_id": "admin_john"
}
```

**Excepciones:**
- `ValueError("Admin ID already exists")` si admin_id duplicado
- `ValueError("Email already registered")` si email duplicado

---

### **3.2 LoginAdminUseCase**

**Flujo:**
1. Buscar admin por `admin_id`
2. Verificar que el admin exista
3. Verificar password con bcrypt
4. Verificar que la cuenta esté activa (`is_active = True`)
5. **CRÍTICO:** Verificar que el email esté verificado (`is_verified = True`)
6. Generar token JWT con payload: `{"sub": admin_id, "email": email, "type": "admin"}`
7. Actualizar `last_login` en MongoDB
8. Retornar token y datos del admin

**Input:**
- `admin_id`: str
- `password`: str

**Output:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "admin_id": "admin_john",
  "email": "john@admin.com",
  "full_name": "John Admin",
  "is_verified": true
}
```

**Excepciones:**
- `ValueError("Invalid credentials")` si admin no existe o password incorrecto
- `ValueError("Admin account is inactive")` si cuenta inactiva
- `ValueError("Debes verificar tu correo electrónico antes de iniciar sesión")` si no verificado

---

### **3.3 VerifyAdminEmailUseCase**

**Flujo:**
1. Buscar admin por `verification_token`
2. Validar que el admin exista
3. Verificar que el token no haya expirado (24 horas)
4. Marcar `is_verified = True`
5. Limpiar `verification_token` y `verification_token_expires`
6. Actualizar admin en MongoDB
7. Enviar email de bienvenida

**Input:**
- `token`: str (código de 6 dígitos)

**Output:**
```json
{
  "success": true,
  "message": "Email verified successfully",
  "admin_id": "admin_john"
}
```

**Excepciones:**
- `ValueError("Invalid verification token")` si token no existe
- `ValueError("Verification token has expired")` si expiró

### **Metodología TDD**
- **Red**: Escribir tests para los 3 casos de uso antes de implementar.
  - Archivo: `tests/unit/test_admin_auth_use_cases.py`
  - Commit: `git commit -m "RED: add failing tests for admin auth use cases"`
  - Push: `git push origin feature/admin-auth`
- **Green**: Implementar RegisterAdminUseCase, LoginAdminUseCase y VerifyAdminEmailUseCase.
  - Commit RegisterAdmin: `git commit -m "GREEN: implement RegisterAdminUseCase"`
  - Commit LoginAdmin: `git commit -m "GREEN: implement LoginAdminUseCase"`
  - Commit VerifyEmail: `git commit -m "GREEN: implement VerifyAdminEmailUseCase"`
  - Push: `git push origin feature/admin-auth`
- **Refactor**: Optimizar lógica de validación y manejo de errores.
  - Commit: `git commit -m "REFACTOR: optimize admin auth use cases validation logic"`
  - Push: `git push origin feature/admin-auth`
- **Ciclo estricto**: Seguir Red → Green → Refactor sin saltarse pasos.
- **Después de cada paso**: Ejecutar `git push` para sincronizar con GitHub.

### **Cobertura**
- **Objetivo**: >70% en admin_auth_use_cases.py
- **Comando**: `pytest tests/unit/test_admin_auth_use_cases.py --cov=services.fraud-evaluation-service.src.application.admin_auth_use_cases --cov-report=html --cov-report=term`
- **Reporte HTML**: `htmlcov/index.html`

### **Tests Específicos**

**RegisterAdminUseCase (5 tests):**
- `test_register_admin_success()`: Registro exitoso con datos válidos
- `test_register_admin_duplicate_admin_id()`: Error con admin_id duplicado
- `test_register_admin_duplicate_email()`: Error con email duplicado
- `test_register_admin_password_hashing()`: Verificar que password se hashea
- `test_register_admin_email_sent()`: Verificar envío de email de verificación

**LoginAdminUseCase (6 tests):**
- `test_login_admin_success()`: Login exitoso con credenciales correctas
- `test_login_admin_invalid_admin_id()`: Error con admin_id no existente
- `test_login_admin_invalid_password()`: Error con password incorrecto
- `test_login_admin_inactive_account()`: Error con cuenta inactiva
- `test_login_admin_unverified_email()`: Error con email no verificado
- `test_login_admin_jwt_payload()`: Verificar contenido del JWT

**VerifyAdminEmailUseCase (3 tests):**
- `test_verify_email_success()`: Verificación exitosa con token válido
- `test_verify_email_invalid_token()`: Error con token inexistente
- `test_verify_email_expired_token()`: Error con token expirado

### **Tests Unitarios**
- **Ruta**: `tests/unit/test_admin_auth_use_cases.py`
- **Cobertura**: >70% en lógica de casos de uso
- **Total de tests**: Mínimo 14 tests

### **Código Limpio y Principios SOLID**
- **0 violaciones a principios SOLID**:
  - **S (Single Responsibility)**: Cada caso de uso tiene una única responsabilidad (Register, Login, Verify).
  - **O (Open/Closed)**: Casos de uso extensibles (agregar más validaciones) sin modificar código existente.
  - **L (Liskov Substitution)**: Todos los casos de uso pueden implementar IUseCase si fuera necesario.
  - **I (Interface Segregation)**: Cada caso de uso solo expone método `execute()`, sin interfaces complejas.
  - **D (Dependency Inversion)**: Dependen de abstracciones (AdminRepository, PasswordService) no de implementaciones concretas.
- **Clean Code**: 
  - Flujos de negocio explícitos y secuenciales
  - Nombres descriptivos (`RegisterAdminUseCase`, `execute()`)
  - Validaciones claras sin condicionales anidados
  - Manejo explícito de excepciones con mensajes claros
  - Sin lógica de infraestructura en casos de uso

### **Entregables**
- ✅ **Característica funcional**: 3 casos de uso completos (Register, Login, Verify)
- ✅ **Tests unitarios**: `tests/unit/test_admin_auth_use_cases.py` con mínimo 14 tests
- ✅ **Reporte de cobertura**: >70% en admin_auth_use_cases.py
- ✅ **Commits TDD**: 5 commits (RED, 3 GREEN, REFACTOR) sincronizados con GitHub

---

## 📝 Paso 4: Crear Rutas de API para Admin

### **Objetivo**
Exponer endpoints REST en el API Gateway para autenticación de administradores.

### **Archivo a Crear**
- `services/api-gateway/src/admin_auth_routes.py`

### **Endpoints a Implementar**

#### **4.1 POST /api/v1/admin/auth/register**

**Request Body:**
```json
{
  "admin_id": "admin_john",
  "email": "john@admin.com",
  "password": "securePassword123",
  "full_name": "John Admin"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Admin registered successfully. Please check your email to verify your account.",
  "admin_id": "admin_john"
}
```

**Errores:**
- `400 Bad Request`: Validación fallida (admin_id o email duplicado)
- `500 Internal Server Error`: Error del servidor

---

#### **4.2 POST /api/v1/admin/auth/login**

**Request Body:**
```json
{
  "admin_id": "admin_john",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "admin_id": "admin_john",
  "email": "john@admin.com",
  "full_name": "John Admin",
  "is_verified": true
}
```

**Errores:**
- `401 Unauthorized`: Credenciales inválidas
- `403 Forbidden`: Cuenta inactiva o email no verificado

---

#### **4.3 POST /api/v1/admin/auth/verify-email**

**Request Body:**
```json
{
  "token": "123456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Email verified successfully",
  "admin_id": "admin_john"
}
```

**Errores:**
- `400 Bad Request`: Token inválido o expirado

---

#### **4.4 GET /api/v1/admin/auth/me** (Protected)

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "admin_id": "admin_john",
  "email": "john@admin.com",
  "full_name": "John Admin",
  "is_verified": true,
  "is_active": true,
  "created_at": "2026-01-19T10:30:00Z"
}
```

**Errores:**
- `401 Unauthorized`: Token inválido o expirado

---

### **Integración en API Gateway**

**Archivo a Modificar:**
- `services/api-gateway/src/main.py`

**Agregar:**
```python
from admin_auth_routes import admin_auth_router

app.include_router(admin_auth_router, prefix="/api/v1/admin/auth", tags=["Admin Auth"])
```

### **Metodología TDD**
- **Red**: Escribir tests de integración para endpoints antes de implementar.
  - Archivo: `tests/integration/test_admin_auth_endpoints.py`
  - Commit: `git commit -m "RED: add failing tests for admin auth API endpoints"`
  - Push: `git push origin feature/admin-auth`
- **Green**: Implementar los 4 endpoints en admin_auth_routes.py.
  - Commit: `git commit -m "GREEN: implement admin auth API endpoints"`
  - Push: `git push origin feature/admin-auth`
- **Refactor**: Optimizar manejo de errores y validaciones.
  - Commit: `git commit -m "REFACTOR: improve error handling in admin auth endpoints"`
  - Push: `git push origin feature/admin-auth`
- **Ciclo estricto**: Seguir Red → Green → Refactor sin saltarse pasos.
- **Después de cada paso**: Ejecutar `git push` para sincronizar con GitHub.

### **Cobertura**
- **Objetivo**: >70% en admin_auth_routes.py
- **Comando**: `pytest tests/integration/test_admin_auth_endpoints.py --cov=services.api-gateway.src.admin_auth_routes --cov-report=html --cov-report=term`
- **Reporte HTML**: `htmlcov/index.html`

### **Tests Específicos**
- `test_register_admin_endpoint_success()`: POST /register retorna 201
- `test_register_admin_endpoint_duplicate()`: POST /register con duplicado retorna 400
- `test_login_admin_endpoint_success()`: POST /login retorna 200 y access_token
- `test_login_admin_endpoint_invalid_credentials()`: POST /login con credenciales incorrectas retorna 401
- `test_verify_email_admin_endpoint_success()`: POST /verify-email retorna 200
- `test_verify_email_admin_endpoint_invalid_token()`: POST /verify-email con token inválido retorna 400
- `test_get_current_admin_endpoint_success()`: GET /me con token válido retorna 200
- `test_get_current_admin_endpoint_unauthorized()`: GET /me sin token retorna 401

### **Tests de Integración**
- **Ruta**: `tests/integration/test_admin_auth_endpoints.py`
- **Cobertura**: >70% en endpoints
- **Total de tests**: Mínimo 8 tests

### **Código Limpio y Principios SOLID**
- **0 violaciones a principios SOLID**:
  - **S (Single Responsibility)**: Cada endpoint solo maneja una operación HTTP específica.
  - **O (Open/Closed)**: Rutas extensibles (agregar más endpoints) sin modificar existentes.
  - **L (Liskov Substitution)**: Todos los endpoints siguen el mismo patrón de FastAPI.
  - **I (Interface Segregation)**: Cada endpoint solo expone lo necesario, sin dependencias innecesarias.
  - **D (Dependency Inversion)**: Endpoints dependen de casos de uso (abstracciones), no de repositorios directos.
- **Clean Code**: 
  - Nombres de endpoints RESTful claros (`/register`, `/login`, `/verify-email`)
  - Status codes HTTP correctos (201 Created, 200 OK, 401 Unauthorized, 400 Bad Request)
  - Manejo consistente de errores con HTTPException
  - Validación de request bodies con Pydantic
  - Documentación automática con OpenAPI

### **Entregables**
- ✅ **Característica funcional**: 4 endpoints REST completamente funcionales
- ✅ **Tests de integración**: `tests/integration/test_admin_auth_endpoints.py` con mínimo 8 tests
- ✅ **Reporte de cobertura**: >70% en admin_auth_routes.py
- ✅ **Commits TDD**: 3 commits (RED, GREEN, REFACTOR) sincronizados con GitHub

---

## 📝 Paso 5: Crear Frontend de Admin (Login)

### **Objetivo**
Implementar páginas de autenticación en el Admin Dashboard (React + TypeScript + Vite).

### **5.1 LoginPage para Admin**

**Archivo a Crear:**
- `frontend/admin-dashboard/src/pages/LoginPage.tsx`

**Componentes:**
- Formulario con campos: `admin_id`, `password`
- Validación de campos requeridos
- Manejo de errores (credenciales inválidas, cuenta no verificada)
- Redirección a Dashboard tras login exitoso
- Link a página de registro
- Diseño consistente con Tailwind CSS

**Flujo:**
1. Usuario ingresa `admin_id` y `password`
2. Submit → POST a `/api/v1/admin/auth/login`
3. Si exitoso: Guardar token en `localStorage`
4. Redirigir a `/dashboard`
5. Si error: Mostrar mensaje de error

**LocalStorage:**
```javascript
localStorage.setItem('admin_token', response.access_token);
localStorage.setItem('admin_id', response.admin_id);
localStorage.setItem('admin_email', response.email);
```

---

### **5.2 RegisterPage para Admin**

**Archivo a Crear:**
- `frontend/admin-dashboard/src/pages/RegisterPage.tsx`

**Componentes:**
- Formulario con campos: `admin_id`, `email`, `password`, `confirmPassword`, `full_name`
- Validación de:
  - Passwords coinciden
  - Password mínimo 6 caracteres
  - Email formato válido
  - admin_id mínimo 3 caracteres
- Manejo de errores (admin_id o email duplicado)
- Redirección a VerifyEmailPage tras registro exitoso

**Flujo:**
1. Admin ingresa datos del formulario
2. Validaciones en frontend
3. Submit → POST a `/api/v1/admin/auth/register`
4. Si exitoso: Redirigir a `/verify-email` con mensaje
5. Si error: Mostrar mensaje (duplicado, validación, etc.)

---

### **5.3 VerifyEmailPage para Admin**

**Archivo a Crear:**
- `frontend/admin-dashboard/src/pages/VerifyEmailPage.tsx`

**Componentes:**
- Input para código de 6 dígitos
- Validación de formato (solo números)
- Botón "Verificar"
- Link para reenviar código (opcional)
- Redirección a LoginPage tras verificación exitosa

**Flujo:**
1. Admin recibe email con código de 6 dígitos
2. Ingresa código en la página
3. Submit → POST a `/api/v1/admin/auth/verify-email`
4. Si exitoso: Mensaje de éxito + redirigir a `/login`
5. Si error: Mostrar mensaje (código inválido, expirado)

---

### **5.4 ProtectedRoute Component**

**Archivo a Crear:**
- `frontend/admin-dashboard/src/components/ProtectedRoute.tsx`

**Propósito:**
Proteger rutas del dashboard que requieren autenticación.

**Lógica:**
```typescript
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('admin_token');
  
  if (!token) {
    // No hay token → redirigir a login
    return <Navigate to="/login" />;
  }
  
  // Hay token → renderizar componente protegido
  return children;
};
```

**Uso:**
```typescript
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

### **Metodología de Desarrollo Frontend**
- **Implementación Incremental**: Crear componentes uno a uno con validaciones.
  - Commit LoginPage: `git commit -m "feat: implement LoginPage for admin dashboard"`
  - Commit RegisterPage: `git commit -m "feat: implement RegisterPage for admin dashboard"`
  - Commit VerifyEmailPage: `git commit -m "feat: implement VerifyEmailPage for admin dashboard"`
  - Commit ProtectedRoute: `git commit -m "feat: implement ProtectedRoute component"`
  - Push después de cada commit: `git push origin feature/admin-auth`
- **Validación Manual**: Probar cada página en el navegador antes de commit.
- **Tests E2E**: Se implementarán en el Paso 10 con Playwright.

### **Tests E2E (Playwright)**
- **Los tests detallados se crearán en el Paso 10**
- **Archivo**: `tests-e2e/tests/admin-auth.spec.ts`
- **Cobertura**: Flujo completo de autenticación (register → verify → login → dashboard)

### **Código Limpio y Principios SOLID (Frontend)**
- **Componentes con responsabilidad única**:
  - LoginPage: Solo maneja login
  - RegisterPage: Solo maneja registro
  - VerifyEmailPage: Solo maneja verificación
  - ProtectedRoute: Solo valida autenticación
- **Reutilización de código**: Componentes compartidos (Form inputs, Buttons, Cards)
- **Nombres descriptivos**: Variables y funciones con nombres claros (`handleLogin`, `validateForm`)
- **Sin lógica duplicada**: Extraer validaciones comunes a funciones helper
- **Manejo de errores consistente**: Mensajes claros al usuario

### **Entregables**
- ✅ **Característica funcional**: 4 componentes React completos y funcionales
- ✅ **Tests E2E**: Se validarán en el Paso 10 con Playwright
- ✅ **Commits**: 4 commits sincronizados con GitHub
- ✅ **Validación manual**: Todas las páginas testeadas en navegador

---

## 📝 Paso 6: Actualizar Rutas del Admin Dashboard

### **Objetivo**
Configurar React Router para manejar rutas de autenticación y rutas protegidas.

### **Archivo a Modificar:**
- `frontend/admin-dashboard/src/App.tsx`

### **Estructura de Rutas Propuesta:**

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas Públicas */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        
        {/* Rutas Protegidas */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        
        <Route path="/transactions" element={
          <ProtectedRoute>
            <TransactionsPage />
          </ProtectedRoute>
        } />
        
        {/* Redirección por defecto */}
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### **Metodología de Desarrollo Frontend**
- **Implementación**: Configurar React Router con todas las rutas.
  - Commit: `git commit -m "feat: configure admin dashboard routes with authentication"`
  - Push: `git push origin feature/admin-auth`
- **Validación Manual**: Probar navegación entre rutas en el navegador.
- **Tests E2E**: La navegación se probará en el Paso 10 con Playwright.

### **Entregables**
- ✅ **Característica funcional**: React Router configurado con rutas públicas y protegidas
- ✅ **Commits**: 1 commit sincronizado con GitHub
- ✅ **Validación manual**: Navegación entre rutas testeada en navegador

---

## 📝 Paso 7: Configurar Axios Interceptor (Opcional)

### **Objetivo**
Agregar token JWT automáticamente a todas las peticiones protegidas.

### **Archivo a Crear:**
- `frontend/admin-dashboard/src/services/api.ts`

### **Configuración:**

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a todas las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores 401 (token expirado)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado → limpiar y redirigir a login
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_id');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

**Uso:**
```typescript
import api from './services/api';

// Ya no necesitas agregar token manualmente
const response = await api.get('/admin/auth/me');
```

### **Metodología de Desarrollo Frontend**
- **Implementación**: Crear archivo api.ts con interceptores de Axios.
  - Commit: `git commit -m "feat: add Axios interceptor for admin authentication"`
  - Push: `git push origin feature/admin-auth`
- **Validación Manual**: Probar peticiones protegidas con/sin token.

### **Entregables**
- ✅ **Característica funcional**: Interceptor que agrega token automáticamente y maneja errores 401
- ✅ **Commits**: 1 commit sincronizado con GitHub
- ✅ **Validación manual**: Peticiones protegidas funcionando correctamente

---

## 📝 Paso 8: Tests Unitarios (Backend)

### **Objetivo**
Garantizar calidad del código con cobertura mínima del 70%.

### **Archivo a Crear:**
- `tests/unit/test_admin_auth_use_cases.py`

### **Tests Requeridos:**

#### **8.1 Tests de RegisterAdminUseCase**

1. ✅ `test_register_admin_success()`
   - Registrar admin correctamente
   - Verificar que se guarda en base de datos
   - Verificar envío de email

2. ✅ `test_register_admin_duplicate_admin_id()`
   - Intentar registrar admin_id existente
   - Esperar `ValueError("Admin ID already exists")`

3. ✅ `test_register_admin_duplicate_email()`
   - Intentar registrar email existente
   - Esperar `ValueError("Email already registered")`

4. ✅ `test_register_admin_password_hashing()`
   - Verificar que password se hashea con bcrypt
   - Verificar que no se guarda en texto plano

5. ✅ `test_register_admin_token_generation()`
   - Verificar que se genera token de 6 dígitos
   - Verificar expiración de 24 horas

---

#### **8.2 Tests de LoginAdminUseCase**

1. ✅ `test_login_admin_success()`
   - Login con credenciales correctas
   - Verificar generación de JWT
   - Verificar actualización de last_login

2. ✅ `test_login_admin_invalid_admin_id()`
   - Login con admin_id no existente
   - Esperar `ValueError("Invalid credentials")`

3. ✅ `test_login_admin_invalid_password()`
   - Login con password incorrecto
   - Esperar `ValueError("Invalid credentials")`

4. ✅ `test_login_admin_inactive_account()`
   - Login con cuenta inactiva
   - Esperar `ValueError("Admin account is inactive")`

5. ✅ `test_login_admin_unverified_email()`
   - Login con email no verificado
   - Esperar `ValueError("Debes verificar tu correo...")`

6. ✅ `test_login_admin_jwt_payload()`
   - Verificar contenido del JWT
   - Debe incluir: `sub`, `email`, `type: "admin"`

---

#### **8.3 Tests de VerifyAdminEmailUseCase**

1. ✅ `test_verify_email_success()`
   - Verificar con token válido
   - Marcar `is_verified = True`
   - Enviar email de bienvenida

2. ✅ `test_verify_email_invalid_token()`
   - Verificar con token inexistente
   - Esperar `ValueError("Invalid verification token")`

3. ✅ `test_verify_email_expired_token()`
   - Verificar con token expirado (>24h)
   - Esperar `ValueError("Verification token has expired")`

---

### **Archivo a Crear:**
- `tests/unit/test_admin_repository.py`

### **Tests de AdminRepository:**

1. ✅ `test_save_admin()`
2. ✅ `test_find_by_admin_id()`
3. ✅ `test_find_by_email()`
4. ✅ `test_admin_exists()`
5. ✅ `test_email_exists()`
6. ✅ `test_find_by_verification_token()`
7. ✅ `test_update_admin()`
8. ✅ `test_unique_constraints()` (admin_id y email únicos)

### **Metodología TDD**
**Nota**: Los tests unitarios para casos de uso y repositorio ya fueron creados en los Pasos 1-3. Este paso consolida todos los tests.

- **Ejecutar todos los tests unitarios**: 
  - Comando: `pytest tests/unit/test_admin_*.py -v`
  - Push: `git push origin feature/admin-auth`
- **Verificar cobertura total**:
  - Comando: `pytest tests/unit/test_admin_*.py --cov=services.fraud-evaluation-service.src --cov-report=html --cov-report=term`
  - Objetivo: >70% en módulos de admin

### **Cobertura Consolidada**
- **Objetivo General**: >70% en todos los módulos de admin (modelo, repositorio, casos de uso)
- **Comando**: `pytest tests/unit/test_admin_*.py --cov --cov-report=html`
- **Reporte HTML**: `htmlcov/index.html`

### **Total de Tests Unitarios**
- test_admin_model.py: 5 tests
- test_admin_repository.py: 11 tests
- test_admin_auth_use_cases.py: 14 tests
- **TOTAL**: 30 tests unitarios mínimo

### **Entregables**
- ✅ **Tests unitarios consolidados**: 30+ tests en `tests/unit/`
- ✅ **Reporte de cobertura**: >70% en módulos admin
- ✅ **Todos los tests pasan**: Sin errores ni fallos

---

## 📝 Paso 9: Tests de Integración (API)

### **Objetivo**
Verificar que los endpoints funcionan correctamente end-to-end.

### **Archivo a Crear:**
- `tests/integration/test_admin_auth_endpoints.py`

### **Tests Requeridos:**

1. ✅ `test_register_admin_endpoint_success()`
   - POST `/api/v1/admin/auth/register`
   - Status: 201 Created

2. ✅ `test_register_admin_endpoint_duplicate()`
   - Registrar admin_id existente
   - Status: 400 Bad Request

3. ✅ `test_login_admin_endpoint_success()`
   - POST `/api/v1/admin/auth/login`
   - Status: 200 OK
   - Retorna access_token

4. ✅ `test_login_admin_endpoint_invalid_credentials()`
   - Login con credenciales incorrectas
   - Status: 401 Unauthorized

5. ✅ `test_verify_email_admin_endpoint_success()`
   - POST `/api/v1/admin/auth/verify-email`
   - Status: 200 OK

6. ✅ `test_get_current_admin_endpoint_success()`
   - GET `/api/v1/admin/auth/me`
   - Con header Authorization
   - Status: 200 OK

7. ✅ `test_get_current_admin_endpoint_unauthorized()`
   - GET sin token
   - Status: 401 Unauthorized

### **Metodología TDD**
**Nota**: Los tests de integración para endpoints fueron creados en el Paso 4. Este paso ejecuta y valida todos los tests.

- **Ejecutar tests de integración**:
  - Comando: `pytest tests/integration/test_admin_auth_endpoints.py -v`
  - Push: `git push origin feature/admin-auth`
- **Verificar cobertura de endpoints**:
  - Comando: `pytest tests/integration/test_admin_auth_endpoints.py --cov=services.api-gateway.src.admin_auth_routes --cov-report=html --cov-report=term`

### **Cobertura**
- **Objetivo**: >70% en admin_auth_routes.py
- **Reporte HTML**: `htmlcov/index.html`

### **Total de Tests de Integración**
- test_admin_auth_endpoints.py: 8 tests mínimo

### **Entregables**
- ✅ **Tests de integración**: 8+ tests validando endpoints REST
- ✅ **Reporte de cobertura**: >70% en admin_auth_routes.py
- ✅ **Todos los tests pasan**: Sin errores ni fallos
- ✅ **API funcional**: Endpoints responden correctamente

---

## 📝 Paso 10: Tests E2E (Frontend)

### **Objetivo**
Probar el flujo completo de autenticación desde el navegador.

### **Archivo a Crear:**
- `tests-e2e/tests/admin-auth.spec.ts`

### **Tests Requeridos con Playwright:**

1. ✅ `TEST-ADMIN-001: Registro completo de administrador`
   - Navegar a `/register`
   - Llenar formulario
   - Verificar redirección a `/verify-email`

2. ✅ `TEST-ADMIN-002: Verificación de email`
   - Navegar a `/verify-email`
   - Ingresar código de 6 dígitos
   - Verificar redirección a `/login`

3. ✅ `TEST-ADMIN-003: Login exitoso`
   - Navegar a `/login`
   - Ingresar admin_id y password
   - Verificar redirección a `/dashboard`
   - Verificar token en localStorage

4. ✅ `TEST-ADMIN-004: Login con credenciales incorrectas`
   - Intentar login con password incorrecto
   - Verificar mensaje de error
   - Permanecer en `/login`

5. ✅ `TEST-ADMIN-005: Acceso a ruta protegida sin token`
   - Intentar acceder a `/dashboard` sin login
   - Verificar redirección a `/login`

6. ✅ `TEST-ADMIN-006: Logout (limpiar token)`
   - Click en botón logout
   - Verificar limpieza de localStorage
   - Verificar redirección a `/login`

### **Metodología de Testing E2E**
- **Implementación**: Escribir tests E2E con Playwright para flujo completo.
  - Archivo: `tests-e2e/tests/admin-auth.spec.ts`
  - Commit: `git commit -m "test: add E2E tests for admin authentication flow"`
  - Push: `git push origin feature/admin-auth`
- **Ejecución**: `npx playwright test tests/admin-auth.spec.ts`
- **Modo visual**: `npx playwright test tests/admin-auth.spec.ts --ui` (para debug)

### **Cobertura E2E**
- **Flujo completo**: Registro → Verificación → Login → Dashboard protegido → Logout
- **Validaciones**: Redirecciones, localStorage, mensajes de error, UI elements

### **Total de Tests E2E**
- admin-auth.spec.ts: 6 tests mínimo

### **Entregables**
- ✅ **Tests E2E completos**: 6+ tests con Playwright validando flujo de autenticación
- ✅ **Todos los tests pasan**: Sin errores en navegador
- ✅ **Screenshots**: Capturas automáticas de cada paso (Playwright)
- ✅ **Commits**: 1 commit sincronizado con GitHub

---

## 📝 Paso 11: Documentación

### **Archivos a Crear/Actualizar:**

#### **11.1 README de Admin Auth**
- `frontend/admin-dashboard/docs/AUTH_FLOW.md`

**Contenido:**
- Diagrama de flujo de autenticación
- Endpoints disponibles
- Ejemplos de uso con cURL
- Troubleshooting común

#### **11.2 Actualizar README Principal**
- `README.md`

**Agregar sección:**
```markdown
## 👤 Autenticación de Administradores

### Crear un Administrador
```bash
curl -X POST http://localhost:8000/api/v1/admin/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": "admin_john",
    "email": "john@admin.com",
    "password": "securePassword123",
    "full_name": "John Admin"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": "admin_john",
    "password": "securePassword123"
  }'
```

### Acceder al Admin Dashboard
1. Abrir http://localhost:3001/
2. Ingresar credenciales
3. Verificar email con código de 6 dígitos
4. Acceder al dashboard
```

#### **11.3 Postman Collection**
- `docs/postman/Admin_Auth_Collection.json`

**Incluir:**
- Todos los endpoints de admin auth
- Variables de entorno
- Tests automatizados

### **Metodología de Documentación**
- **Crear documentación completa**:
  - Commit AUTH_FLOW.md: `git commit -m "docs: add admin authentication flow documentation"`
  - Commit README.md: `git commit -m "docs: update README with admin auth instructions"`
  - Commit Postman: `git commit -m "docs: add Postman collection for admin auth"`
  - Push: `git push origin feature/admin-auth`

### **Entregables**
- ✅ **AUTH_FLOW.md**: Documentación técnica del flujo de autenticación
- ✅ **README.md actualizado**: Instrucciones de uso para administradores
- ✅ **Postman Collection**: Colección completa para testing manual
- ✅ **Commits**: 3 commits sincronizados con GitHub

---
- Todos los endpoints de admin auth
- Variables de entorno
- Tests automatizados

---

## 📊 Estructura de Archivos Final

```
services/
├── fraud-evaluation-service/
│   └── src/
│       ├── domain/
│       │   └── models.py                    # ✅ Agregar Admin entity
│       ├── application/
│       │   └── admin_auth_use_cases.py      # ✅ NUEVO (3 casos de uso)
│       └── infrastructure/
│           └── admin_repository.py          # ✅ NUEVO
│
└── api-gateway/
    └── src/
        ├── admin_auth_routes.py             # ✅ NUEVO (4 endpoints)
        └── main.py                          # ✅ Modificar (incluir router)

frontend/
└── admin-dashboard/
    └── src/
        ├── pages/
        │   ├── LoginPage.tsx                # ✅ NUEVO
        │   ├── RegisterPage.tsx             # ✅ NUEVO
        │   └── VerifyEmailPage.tsx          # ✅ NUEVO
        ├── components/
        │   └── ProtectedRoute.tsx           # ✅ NUEVO
        ├── services/
        │   └── api.ts                       # ✅ NUEVO (Axios config)
        └── App.tsx                          # ✅ Modificar (rutas)

tests/
├── unit/
│   ├── test_admin_auth_use_cases.py        # ✅ NUEVO (15+ tests)
│   └── test_admin_repository.py            # ✅ NUEVO (8+ tests)
├── integration/
│   └── test_admin_auth_endpoints.py        # ✅ NUEVO (7+ tests)
└── e2e/
    └── tests/
        └── admin-auth.spec.ts              # ✅ NUEVO (6+ tests)

docs/
├── postman/
│   └── Admin_Auth_Collection.json          # ✅ NUEVO
└── AUTH_FLOW_ADMIN.md                      # ✅ NUEVO
```

---

## 🔄 Flujo Completo de Autenticación

```
┌─────────────────────────────────────────────────────────────────────┐
│                    REGISTRO DE ADMINISTRADOR                         │
└─────────────────────────────────────────────────────────────────────┘

1️⃣  Admin Dashboard (Frontend)
    └─> RegisterPage.tsx
        └─> Usuario ingresa: admin_id, email, password, full_name
        └─> POST /api/v1/admin/auth/register
            ↓
2️⃣  API Gateway
    └─> admin_auth_routes.py
        └─> register_admin()
            ↓
3️⃣  Caso de Uso
    └─> RegisterAdminUseCase.execute()
        ├─> Validar admin_id no existe
        ├─> Validar email no existe
        ├─> Hashear password (bcrypt)
        ├─> Generar token de 6 dígitos
        ├─> Crear entidad Admin
        ├─> Guardar en MongoDB (colección "admins")
        └─> Enviar email con código
            ↓
4️⃣  Infraestructura
    ├─> AdminRepository.save_admin()
    │   └─> MongoDB: admins.insert_one()
    └─> EmailService.send_verification_email()
        └─> SMTP: Enviar correo
            ↓
5️⃣  Email del Administrador
    └─> Recibe código: "123456"
        └─> Abre VerifyEmailPage
            ↓
6️⃣  Verificación de Email
    └─> POST /api/v1/admin/auth/verify-email
        └─> VerifyAdminEmailUseCase.execute()
            ├─> Buscar por token
            ├─> Validar no expirado
            ├─> Marcar is_verified = True
            └─> Enviar email de bienvenida
                ↓
7️⃣  Login
    └─> LoginPage.tsx
        └─> Usuario ingresa: admin_id, password
        └─> POST /api/v1/admin/auth/login
            └─> LoginAdminUseCase.execute()
                ├─> Buscar admin
                ├─> Verificar password
                ├─> Verificar is_verified = True
                ├─> Generar JWT
                └─> Retornar token
                    ↓
8️⃣  Dashboard Protegido
    └─> Guardar token en localStorage
    └─> ProtectedRoute valida token
    └─> Renderizar Dashboard
        └─> Todas las peticiones incluyen:
            Authorization: Bearer <token>

┌─────────────────────────────────────────────────────────────────────┐
│                    PROTECCIÓN DE RUTAS                               │
└─────────────────────────────────────────────────────────────────────┘

1️⃣  Usuario intenta acceder a /dashboard
    ↓
2️⃣  ProtectedRoute.tsx
    └─> Verifica token en localStorage
    ├─> ✅ Token existe → Renderizar Dashboard
    └─> ❌ No hay token → Redirigir a /login
        ↓
3️⃣  Peticiones Protegidas
    └─> api.ts (Axios Interceptor)
        └─> Agrega header: Authorization: Bearer <token>
            ↓
4️⃣  API Gateway
    └─> get_current_admin_from_token()
        ├─> Extraer token del header
        ├─> Verificar con JWTService
        ├─> Validar payload
        └─> Retornar admin_id
            ↓
5️⃣  Endpoint Protegido
    └─> Procesar petición con admin_id validado
```

---

## 📋 Checklist de Implementación

### **Backend**

- [ ] **Paso 1**: Crear entidad `Admin` en `models.py`
- [ ] **Paso 2**: Implementar `AdminRepository`
- [ ] **Paso 3**: Implementar `RegisterAdminUseCase`
- [ ] **Paso 3**: Implementar `LoginAdminUseCase`
- [ ] **Paso 3**: Implementar `VerifyAdminEmailUseCase`
- [ ] **Paso 4**: Crear `admin_auth_routes.py` con 4 endpoints
- [ ] **Paso 4**: Integrar router en `main.py`
- [ ] **Paso 8**: Escribir tests unitarios (23+ tests)
- [ ] **Paso 9**: Escribir tests de integración (7+ tests)
- [ ] **Validación**: Ejecutar todos los tests y verificar cobertura >85%

### **Frontend**

- [ ] **Paso 5**: Crear `LoginPage.tsx`
- [ ] **Paso 5**: Crear `RegisterPage.tsx`
- [ ] **Paso 5**: Crear `VerifyEmailPage.tsx`
- [ ] **Paso 5**: Crear `ProtectedRoute.tsx`
- [ ] **Paso 6**: Configurar rutas en `App.tsx`
- [ ] **Paso 7**: Crear `api.ts` con Axios interceptors
- [ ] **Paso 10**: Escribir tests E2E (6+ tests)
- [ ] **Validación**: Ejecutar Playwright y verificar todos pasan

### **Documentación**

- [ ] **Paso 11**: Crear `AUTH_FLOW_ADMIN.md`
- [ ] **Paso 11**: Actualizar `README.md` principal
- [ ] **Paso 11**: Crear Postman Collection

### **Integración y Despliegue**

- [ ] Verificar que MongoDB tenga colección `admins`
- [ ] Verificar índices únicos creados
- [ ] Probar flujo completo manualmente
- [ ] Verificar emails se envían correctamente
- [ ] Verificar tokens JWT funcionan
- [ ] Ejecutar suite completa de tests (unit + integration + E2E)
- [ ] Verificar cobertura de código (objetivo: >85%)

---

## ⚠️ Consideraciones Importantes

### **Seguridad**

1. **Passwords**: Siempre hasheados con bcrypt (10 rounds)
2. **JWT**: Expiración de 30 minutos (configurable)
3. **Tokens de verificación**: Expiración de 24 horas
4. **HTTPS**: Requerido en producción
5. **CORS**: Configurar correctamente para frontend en puerto 3001
6. **Rate Limiting**: Implementar en endpoints de login (opcional, Fase 2)

### **Separación de Datos**

- **Usuarios**: Colección `users` en MongoDB
- **Administradores**: Colección `admins` en MongoDB
- **Sin roles**: Un admin es un admin, punto
- **JWT diferenciado**: Incluir `"type": "admin"` en payload para auditoría

### **Email**

- **SMTP**: Configurar variables de entorno:
  ```
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=tu_email@gmail.com
  SMTP_PASSWORD=tu_app_password
  ```
- **Templates**: Reutilizar templates existentes de usuarios
- **Asunto**: Cambiar a "Verificación de Admin - FinTech"

### **Frontend**

- **LocalStorage**: Almacenar token, admin_id, email
- **Redirecciones**: Automáticas tras cada paso
- **UX**: Mensajes claros de error y éxito
- **Diseño**: Consistente con el resto del Admin Dashboard

---

## 📊 Estimación de Esfuerzo

| Tarea | Tiempo Estimado | Prioridad |
|-------|----------------|-----------|
| Modelo Admin + Repository | 3 horas | Alta |
| Casos de Uso (3) | 5 horas | Alta |
| API Routes (4 endpoints) | 3 horas | Alta |
| Frontend LoginPage | 2 horas | Alta |
| Frontend RegisterPage | 2 horas | Alta |
| Frontend VerifyEmailPage | 2 horas | Alta |
| ProtectedRoute + Routing | 2 horas | Alta |
| Axios Interceptor | 1 hora | Media |
| Tests Unitarios (Backend) | 4 horas | Alta |
| Tests Integración (API) | 3 horas | Alta |
| Tests E2E (Playwright) | 3 horas | Alta |
| Documentación | 2 horas | Media |
| Testing Manual + Ajustes | 3 horas | Alta |
| **TOTAL** | **35 horas** | **(~1 semana)** |

---

## 🎯 Criterios de Aceptación

### **Backend**

✅ Todos los endpoints de admin auth funcionan correctamente  
✅ Administradores se guardan en colección separada `admins`  
✅ Passwords hasheados con bcrypt  
✅ JWT generados con payload correcto (`type: "admin"`)  
✅ Email de verificación enviado con código de 6 dígitos  
✅ Validación de email obligatoria antes de login  
✅ Tests unitarios con cobertura >85%  
✅ Tests de integración todos pasan  

### **Frontend**

✅ Páginas de login, registro y verificación funcionan  
✅ Validaciones de formulario correctas  
✅ Mensajes de error claros y útiles  
✅ Token guardado en localStorage tras login  
✅ ProtectedRoute redirige correctamente  
✅ Axios agrega token automáticamente  
✅ Tests E2E con Playwright todos pasan  

### **Documentación**

✅ README actualizado con ejemplos de uso  
✅ Postman Collection creada y funcional  
✅ Diagramas de flujo claros  

---

## 🚀 Próximos Pasos (Fases Futuras)

### **Fase 2: Gestión de Administradores**

- Listar todos los administradores
- Activar/desactivar cuentas
- Resetear contraseñas
- Logs de acceso de admins

### **Fase 3: Permisos Granulares (Opcional)**

- Implementar roles: `super_admin`, `analyst`, `support`
- Permisos por módulo
- Auditoría detallada de acciones

### **Fase 4: Multi-Factor Authentication (MFA)**

- TOTP con Google Authenticator
- SMS verification
- Backup codes

---

## � Resumen de Metodología TDD y Principios SOLID

### **Metodología TDD Aplicada en FASE 1**

Cada paso de implementación sigue estrictamente el ciclo **Red → Green → Refactor**:

| Paso | Componente | Tests Red | Tests Green | Tests Refactor | Total Tests |
|------|------------|-----------|-------------|----------------|-------------|
| 1 | Admin Entity | `test_admin_model.py` | Implementar modelo | Optimizar validaciones | 5 tests |
| 2 | AdminRepository | `test_admin_repository.py` | Implementar CRUD | Optimizar queries | 11 tests |
| 3 | Admin Use Cases | `test_admin_auth_use_cases.py` | Implementar 3 casos de uso | Optimizar lógica | 14 tests |
| 4 | API Endpoints | `test_admin_auth_endpoints.py` | Implementar 4 endpoints | Mejorar errores | 8 tests |
| 10 | E2E Frontend | `admin-auth.spec.ts` | Implementar flujo completo | Optimizar UX | 6 tests |
| **TOTAL** | **5 Componentes** | **44 Tests** | **44 Tests** | **44 Tests** | **44 Tests** |

### **Ciclo TDD por Componente**

```
┌─────────────────────────────────────────────────────────────┐
│                    CICLO TDD ESTRICTO                        │
└─────────────────────────────────────────────────────────────┘

1️⃣  RED (Escribir tests que fallan)
    ├─> Escribir test para funcionalidad nueva
    ├─> Ejecutar test → ❌ Falla (esperado)
    ├─> Commit: "RED: add failing test for [feature]"
    └─> Push: git push origin feature/admin-auth

2️⃣  GREEN (Implementar código mínimo para pasar tests)
    ├─> Escribir código para pasar el test
    ├─> Ejecutar test → ✅ Pasa
    ├─> Commit: "GREEN: implement [feature]"
    └─> Push: git push origin feature/admin-auth

3️⃣  REFACTOR (Optimizar sin romper tests)
    ├─> Mejorar código manteniendo tests verdes
    ├─> Ejecutar tests → ✅ Todos pasan
    ├─> Commit: "REFACTOR: optimize [feature] logic"
    └─> Push: git push origin feature/admin-auth

🔄 REPETIR para cada funcionalidad nueva
```

### **Comandos de Cobertura por Módulo**

**Backend:**
```bash
# Modelo Admin
pytest tests/unit/test_admin_model.py --cov=services.fraud-evaluation-service.src.domain.models --cov-report=html

# AdminRepository
pytest tests/unit/test_admin_repository.py --cov=services.fraud-evaluation-service.src.infrastructure.admin_repository --cov-report=html

# Casos de Uso
pytest tests/unit/test_admin_auth_use_cases.py --cov=services.fraud-evaluation-service.src.application.admin_auth_use_cases --cov-report=html

# API Endpoints
pytest tests/integration/test_admin_auth_endpoints.py --cov=services.api-gateway.src.admin_auth_routes --cov-report=html

# Cobertura TOTAL del backend
pytest tests/ --cov=services --cov-report=html --cov-report=term
```

**Frontend (E2E):**
```bash
# Tests E2E con Playwright
npx playwright test tests/admin-auth.spec.ts

# Modo UI (para debugging)
npx playwright test tests/admin-auth.spec.ts --ui

# Con screenshots automáticos
npx playwright test tests/admin-auth.spec.ts --screenshot=on
```

### **Principios SOLID en cada Componente**

| Componente | S | O | L | I | D | Clean Code |
|------------|---|---|---|---|---|------------|
| **Admin Entity** | ✅ Solo representa admin | ✅ Extensible por herencia | ✅ Sustituible como entidad | ✅ Sin interfaces innecesarias | ✅ Sin dependencias concretas | ✅ Nombres descriptivos |
| **AdminRepository** | ✅ Solo persistencia | ✅ Agregar métodos sin modificar | ✅ Implementa IRepository | ✅ Métodos específicos CRUD | ✅ Depende de abstracciones | ✅ Queries optimizadas |
| **Use Cases** | ✅ Una responsabilidad por caso | ✅ Agregar validaciones sin modificar | ✅ Todos implementan execute() | ✅ Solo método execute() | ✅ Depende de repositorios (abstracción) | ✅ Flujos explícitos |
| **API Endpoints** | ✅ Un endpoint por operación | ✅ Agregar endpoints sin modificar | ✅ Siguen patrón FastAPI | ✅ Solo lo necesario en cada ruta | ✅ Depende de use cases | ✅ RESTful, status codes correctos |
| **Frontend Components** | ✅ Un componente por página | ✅ Agregar props sin romper | ✅ React components | ✅ Props específicas | ✅ Depende de api.ts | ✅ Nombres descriptivos, sin duplicación |

### **Objetivos de Cobertura**

| Tipo de Test | Archivo | Cobertura Objetivo | Tests Mínimos |
|--------------|---------|-------------------|---------------|
| Unitario | test_admin_model.py | >70% | 5 |
| Unitario | test_admin_repository.py | >70% | 11 |
| Unitario | test_admin_auth_use_cases.py | >70% | 14 |
| Integración | test_admin_auth_endpoints.py | >70% | 8 |
| E2E | admin-auth.spec.ts | Flujo completo | 6 |
| **TOTAL** | **5 archivos** | **>70%** | **44 tests** |

### **Estructura de Tests en el Proyecto**

```
tests/
├── unit/                                    # Tests unitarios (>70% cobertura)
│   ├── test_admin_model.py                 # 5 tests - Modelo Admin
│   ├── test_admin_repository.py            # 11 tests - Persistencia
│   └── test_admin_auth_use_cases.py        # 14 tests - Lógica de negocio
│
├── integration/                             # Tests de integración API
│   └── test_admin_auth_endpoints.py        # 8 tests - Endpoints REST
│
└── coverage/                                # Reportes de cobertura
    └── htmlcov/
        └── index.html                       # Reporte HTML navegable

tests-e2e/
└── tests/
    └── admin-auth.spec.ts                   # 6 tests E2E - Flujo completo
```

### **Flujo de Commits TDD**

**Total de commits esperados: ~20 commits**

```bash
# Paso 1: Admin Entity
git commit -m "RED: add failing test for Admin entity model"
git commit -m "GREEN: implement Admin entity model"
git commit -m "REFACTOR: optimize Admin entity validations"

# Paso 2: AdminRepository
git commit -m "RED: add failing tests for AdminRepository"
git commit -m "GREEN: implement AdminRepository with MongoDB"
git commit -m "REFACTOR: optimize AdminRepository queries and error handling"

# Paso 3: Use Cases (3 casos de uso = 3 GREEN commits)
git commit -m "RED: add failing tests for admin auth use cases"
git commit -m "GREEN: implement RegisterAdminUseCase"
git commit -m "GREEN: implement LoginAdminUseCase"
git commit -m "GREEN: implement VerifyAdminEmailUseCase"
git commit -m "REFACTOR: optimize admin auth use cases validation logic"

# Paso 4: API Endpoints
git commit -m "RED: add failing tests for admin auth API endpoints"
git commit -m "GREEN: implement admin auth API endpoints"
git commit -m "REFACTOR: improve error handling in admin auth endpoints"

# Paso 5: Frontend Components (4 componentes)
git commit -m "feat: implement LoginPage for admin dashboard"
git commit -m "feat: implement RegisterPage for admin dashboard"
git commit -m "feat: implement VerifyEmailPage for admin dashboard"
git commit -m "feat: implement ProtectedRoute component"

# Paso 6: Routing
git commit -m "feat: configure admin dashboard routes with authentication"

# Paso 7: Axios Interceptor
git commit -m "feat: add Axios interceptor for admin authentication"

# Paso 10: E2E Tests
git commit -m "test: add E2E tests for admin authentication flow"

# Paso 11: Documentación (3 commits)
git commit -m "docs: add admin authentication flow documentation"
git commit -m "docs: update README with admin auth instructions"
git commit -m "docs: add Postman collection for admin auth"

# TOTAL: ~20 commits siguiendo TDD y buenas prácticas
```

---

## �📞 Contacto y Soporte

**Desarrollador Principal:** Nevardo Ospina  
**Proyecto:** FinTech - Sistema de Detección de Fraude  
**Repositorio:** https://github.com/osp1n4/FinTech  
**Documentación:** `docs/` en el repositorio  

---

## ✅ Conclusión

Este plan describe **todos los pasos necesarios** para implementar autenticación completa de administradores en el Admin Dashboard (http://localhost:3001/), reutilizando la arquitectura existente y manteniendo la simplicidad sin sistema de roles.

### **Características del Plan**

✅ **Metodología TDD estricta**: Ciclo Red → Green → Refactor en cada paso  
✅ **44 tests mínimo**: 30 unitarios + 8 integración + 6 E2E  
✅ **Cobertura >70%**: En todos los módulos backend  
✅ **0 violaciones SOLID**: Cada componente sigue principios SOLID  
✅ **Clean Code**: Código limpio, legible y mantenible  
✅ **~20 commits**: Con mensajes claros siguiendo convenciones  
✅ **Git push después de cada paso**: Sincronización continua con GitHub  

### **Números del Proyecto**

**Tiempo estimado:** 1 semana (35 horas)  
**Archivos nuevos:** 12 archivos  
**Archivos modificados:** 3 archivos  
**Tests totales:** 44+ tests  
**Commits esperados:** ~20 commits  
**Cobertura objetivo:** >70% backend  
**Líneas de código estimadas:** ~2,500 líneas (backend + frontend)  

### **Tecnologías Utilizadas**

**Backend:**
- Python 3.11+
- FastAPI
- MongoDB
- Bcrypt (password hashing)
- JWT (tokens)
- Pytest (testing)
- Coverage.py (cobertura)

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Axios
- React Router v6
- Playwright (E2E)

### **Entregables Finales**

✅ **Backend completo**: Modelo + Repository + Use Cases + API  
✅ **Frontend completo**: Login + Register + Verify + Protected Routes  
✅ **Tests completos**: 44+ tests (unit + integration + E2E)  
✅ **Cobertura >70%**: En todos los módulos backend  
✅ **Documentación completa**: README + AUTH_FLOW + Postman Collection  
✅ **Git sincronizado**: Todos los commits en GitHub  

---

**Estado:** ✅ PLAN COMPLETO - LISTO PARA IMPLEMENTACIÓN CON TDD
