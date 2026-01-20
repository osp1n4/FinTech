# 🏦 FinTech – Sistema de Autenticación Admin
## Plan de Implementación

**Arquitectura:** Microservicios + Event-Driven  


---
## 1️⃣ Fase 1 – Login para Admin Dashboard
**Objetivo:** Login para Admin Dashboard (localhost:3001) reutilizando arquitectura existente

## Paso 1 – Backend (Models + Repository)

### Objetivo
Crear entidad Admin y persistencia MongoDB.

### Actividades
- Crear `Admin` entity (models.py)
- Implementar `AdminRepository` con 8 métodos CRUD
- Configurar colección `admins` con índices únicos

### Metodología TDD
- **Red**: Tests fallan → Commit + Push
- **Green**: Implementar mínimo → Commit + Push
- **Refactor**: Optimizar → Commit + Push
- **Cobertura**: >70% en lógica de negocio

### Código Limpio y SOLID
- **S**: Admin solo representa administrador
- **O**: Extensible sin modificación
- **D**: Depende de abstracciones (pymongo)

### Entregables
- Admin entity funcional
- AdminRepository (save, find, exists, update)
- 26 tests unitarios (13 model + 13 repository)

---

## Paso 2 – Backend (Use Cases + API)

### Objetivo
Lógica de negocio y endpoints REST.

### Actividades
- Implementar 3 use cases:
  - RegisterAdminUseCase (validación + email verificación)
  - LoginAdminUseCase (JWT + verificación email)
  - VerifyAdminEmailUseCase (token 6 dígitos)
- Crear 4 endpoints REST en `admin_auth_routes.py`
- Integrar router en `main.py`

### Endpoints
- POST `/api/v1/admin/auth/register` (201)
- POST `/api/v1/admin/auth/login` (200)
- POST `/api/v1/admin/auth/verify-email` (200)
- GET `/api/v1/admin/auth/me` (200, protected)

### Metodología TDD
- **Red**: Tests integración HTTP fallan
- **Green**: Implementar endpoints
- **Refactor**: Optimizar error handling
- **Cobertura**: >70%

### Entregables
- 3 use cases funcionales
- 4 endpoints REST
- 14 tests unitarios + 9 tests integración

---

## Paso 3 – Frontend

### Objetivo
UI para login/registro/verificación.

### Actividades
- Crear 4 componentes React:
  - LoginPage (admin_id + password)
  - RegisterPage (form + validaciones)
  - VerifyEmailPage (código 6 dígitos)
  - ProtectedRoute (guard con localStorage)
- Configurar rutas en `App.tsx`

### Metodología TDD
- Tests vitest para validaciones frontend
- Integración con backend via fetch

### Entregables
- 4 páginas funcionales
- Rutas públicas y protegidas
- Navegación completa

---

## Paso 4 – Testing E2E y Documentación

### Objetivo
Validar flujo completo y documentar.

### Actividades
- Tests E2E con Playwright (6 tests)
- Crear `AUTH_FLOW_ADMIN.md` con diagramas
- Actualizar README
- Postman collection con 4 endpoints

### Entregables
- Tests E2E funcionales
- Documentación técnica
- Guía de uso

---

## 🧰 Stack Tecnológico

### Backend
- Python 3.11, FastAPI, MongoDB
- JWT, Bcrypt, SMTP

### Frontend
- React + TypeScript, Vite
- React Router, Tailwind CSS

### Testing
- pytest, pytest-cov, Playwright

### Herramientas
- Docker Compose, Git, Postman

---

## 📊 Métricas de Éxito

| Métrica | Objetivo | Estado |
|---------|----------|--------|
| Cobertura | >70% | ✅ |
| Tests Unitarios | 40+ | ✅ 40 |
| Tests Integración | 9+ | ✅ 9 |
| Tests E2E | 6+ | ⏳ |
| SOLID | 0 violaciones | ✅ |

---

## 📋 Principios Aplicados

### TDD
- Red → Green → Refactor
- Tests primero, cobertura >70%

### SOLID
- **S**: Single Responsibility
- **O**: Open/Closed
- **D**: Dependency Inversion

### Clean Code
- Nombres descriptivos
- Sin duplicación
- Commits atómicos
