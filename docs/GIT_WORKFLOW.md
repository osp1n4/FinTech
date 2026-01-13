# 🌿 Flujo de Trabajo Git - Fraud Detection Engine

## 📋 Estrategia de Ramas

Este proyecto utiliza una estrategia de ramas basada en **Gitflow adaptado para microservicios**, diseñada para un equipo pequeño (1-3 desarrolladores) con arquitectura de microservicios.

---

## 🌳 Estructura de Ramas

### Ramas Principales (Permanentes)

#### `main`
- **Propósito:** Código en producción o listo para producción
- **Protección:** ✅ Requiere Pull Request y revisión
- **Merges desde:** `develop` únicamente
- **Nunca hacer commit directo en main**

#### `develop`
- **Propósito:** Rama de integración para desarrollo activo
- **Protección:** ⚠️ Recomendado Pull Request para cambios grandes
- **Merges desde:** Ramas `feature/*`
- **Estado:** Siempre debe ser funcional y pasar todos los tests

---

### Ramas de Funcionalidad (Temporales)

#### Por Microservicio

Cada microservicio tiene su rama dedicada para desarrollo aislado:

```
feature/api-gateway              # API Gateway Service
feature/fraud-evaluation-service # Motor de Evaluación de Fraude
feature/worker-service           # Worker RabbitMQ
feature/frontend-user            # Frontend Usuario (puerto 3000)
feature/frontend-admin           # Frontend Admin (puerto 3001)
```

#### Por Funcionalidad Transversal

Para cambios que afectan múltiples microservicios:

```
feature/authentication           # Sistema de autenticación
feature/monitoring              # Observabilidad y métricas
feature/database-migration      # Cambios en base de datos
feature/ci-cd                   # Pipeline de CI/CD
```

#### Por Bug o Hotfix

Para correcciones urgentes:

```
bugfix/api-gateway-timeout      # Fix en API Gateway
hotfix/security-vulnerability   # Parche de seguridad urgente
```

---

## 🔄 Flujo de Trabajo Diario

### 1. Trabajar en una Funcionalidad

```powershell
# 1. Asegurarse de estar en develop actualizado
git checkout develop
git pull origin develop

# 2. Crear o cambiar a la rama del microservicio
git checkout feature/api-gateway

# 3. Sincronizar con develop si hay cambios recientes
git merge develop

# 4. Hacer tus cambios
# ... editar código ...

# 5. Commitear con mensajes descriptivos
git add services/api-gateway/
git commit -m "feat(api-gateway): Add rate limiting middleware"

# 6. Hacer push frecuentemente
git push origin feature/api-gateway
```

### 2. Integrar Cambios a Develop

```powershell
# Opción A: Merge directo (solo desarrollador, cambios pequeños)
git checkout develop
git merge feature/api-gateway
git push origin develop

# Opción B: Pull Request (recomendado, cambios grandes)
# 1. Push de la rama feature
git push origin feature/api-gateway

# 2. Ir a GitHub y crear Pull Request
# 3. Revisar cambios (o pedir revisión si hay equipo)
# 4. Merge via GitHub UI
```

### 3. Crear Release (Deploy a Producción)

```powershell
# 1. Verificar que develop está estable
git checkout develop
git pull origin develop

# 2. Ejecutar todos los tests
docker-compose up -d
pytest tests/ --cov
npm --prefix frontend/user-app test
npm --prefix frontend/admin-dashboard test

# 3. Hacer merge a main
git checkout main
git merge develop -m "release: Version 1.0.0 - Initial microservices architecture"

# 4. Crear tag de versión
git tag -a v1.0.0 -m "Version 1.0.0: MVP with 3 microservices and 2 frontends"

# 5. Push a remoto
git push origin main
git push origin v1.0.0
```

---

## 📝 Convenciones de Commits

Usamos **Conventional Commits** para mensajes claros y automatización:

```
<tipo>(<alcance>): <descripción breve>

[cuerpo opcional]

[footer opcional]
```

### Tipos de Commit

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formateo, sin cambio de lógica
- `refactor`: Refactorización sin cambiar funcionalidad
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento (dependencias, config)
- `perf`: Mejora de performance
- `ci`: Cambios en CI/CD

### Alcances Sugeridos

- `api-gateway`
- `fraud-service`
- `worker`
- `frontend-user`
- `frontend-admin`
- `shared`
- `infrastructure`
- `docs`

### Ejemplos

```bash
# ✅ Buenos commits
git commit -m "feat(api-gateway): Add transaction endpoint with 202 Accepted"
git commit -m "fix(fraud-service): Correct distance calculation in LocationStrategy"
git commit -m "docs(readme): Update installation instructions for Docker"
git commit -m "test(use-cases): Add edge cases for null locations"
git commit -m "refactor(shared): Extract common models to shared module"

# ❌ Malos commits
git commit -m "fix bug"
git commit -m "cambios varios"
git commit -m "WIP"
git commit -m "asdfasdf"
```

---

## 🎯 Casos de Uso Comunes

### Caso 1: Desarrollar Nueva Funcionalidad en API Gateway

```powershell
git checkout develop
git pull origin develop
git checkout feature/api-gateway
git merge develop  # Sincronizar con cambios recientes

# Hacer cambios en services/api-gateway/
git add services/api-gateway/
git commit -m "feat(api-gateway): Add audit filter by date range"
git push origin feature/api-gateway

# Cuando esté listo
git checkout develop
git merge feature/api-gateway
git push origin develop
```

### Caso 2: Cambio que Afecta Múltiples Microservicios

```powershell
# Crear rama transversal
git checkout develop
git checkout -b feature/add-metrics

# Hacer cambios en api-gateway, fraud-service, worker
git add services/api-gateway/ services/fraud-evaluation-service/ services/worker-service/
git commit -m "feat(shared): Add Prometheus metrics endpoint to all services"
git push origin feature/add-metrics

# Crear Pull Request en GitHub
# Merge a develop cuando esté revisado
```

### Caso 3: Hotfix Urgente en Producción

```powershell
# Crear rama desde main
git checkout main
git pull origin main
git checkout -b hotfix/security-patch

# Hacer el fix
git add .
git commit -m "fix(api-gateway): Patch SQL injection vulnerability"

# Merge directo a main y develop
git checkout main
git merge hotfix/security-patch
git tag -a v1.0.1 -m "Hotfix: Security patch"
git push origin main --tags

git checkout develop
git merge hotfix/security-patch
git push origin develop

# Eliminar rama temporal
git branch -d hotfix/security-patch
git push origin --delete hotfix/security-patch
```

### Caso 4: Resolver Conflictos de Merge

```powershell
git checkout feature/api-gateway
git merge develop  # Conflicto!

# Git marca los archivos en conflicto
# Abrir archivos y resolver manualmente

git add <archivo-resuelto>
git commit -m "merge: Resolve conflicts from develop"
git push origin feature/api-gateway
```

---

## 🛡️ Protección de Ramas (Configuración en GitHub)

### Para `main`:
- ✅ Require pull request before merging
- ✅ Require status checks to pass (CI pipeline)
- ✅ Require branches to be up to date before merging
- ✅ Do not allow bypassing the above settings

### Para `develop`:
- ⚠️ (Opcional) Require pull request for major changes
- ✅ Require status checks to pass

### Para `feature/*`:
- ❌ Sin protección (libertad para experimentar)

---

## 🧹 Limpieza de Ramas

### Ramas Feature Obsoletas (después de merge a develop)

```powershell
# Listar ramas ya mergeadas
git branch --merged develop

# Eliminar ramas locales obsoletas
git branch -d feature/old-feature

# Eliminar ramas remotas obsoletas
git push origin --delete feature/old-feature

# Limpiar referencias remotas obsoletas
git fetch --prune
```

### Ramas Antiguas a Conservar

Las siguientes ramas **NO deben eliminarse** incluso después de merge:
- `feature/api-gateway`
- `feature/fraud-evaluation-service`
- `feature/worker-service`
- `feature/frontend-user`
- `feature/frontend-admin`

Estas son ramas "vivas" por microservicio y se reutilizan continuamente.

---

## 📊 Visualizar Historial de Ramas

```powershell
# Ver gráfico de ramas
git log --oneline --graph --all --decorate

# Ver solo últimas 20 commits
git log --oneline --graph --all --decorate -20

# Ver cambios entre ramas
git diff develop..feature/api-gateway

# Ver archivos modificados entre ramas
git diff --name-only develop..feature/api-gateway
```

---

## 🚨 Comandos de Emergencia

### Deshacer Último Commit (sin perder cambios)

```powershell
git reset --soft HEAD~1
```

### Deshacer Cambios No Commiteados

```powershell
# Descartar cambios en archivo específico
git restore <archivo>

# Descartar todos los cambios
git restore .
```

### Recuperar Commit Eliminado

```powershell
# Ver historial completo (incluye commits "borrados")
git reflog

# Restaurar commit
git cherry-pick <commit-hash>
```

### Cambiar Mensaje del Último Commit

```powershell
git commit --amend -m "nuevo mensaje"
```

---

## ✅ Checklist Antes de Merge a Main

- [ ] Todos los tests pasan (unit, integration, e2e)
- [ ] Cobertura de tests ≥70%
- [ ] SonarQube sin issues críticos
- [ ] Docker Compose funciona correctamente
- [ ] Documentación actualizada (README, docs/)
- [ ] Versión actualizada en pyproject.toml y package.json
- [ ] Tag de versión creado (vX.Y.Z)
- [ ] Changelog actualizado (si existe)

---

## 📚 Referencias

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Gitflow Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Semantic Versioning](https://semver.org/)

---

**Documento creado:** Enero 8, 2026  
**Última actualización:** Enero 8, 2026  
**Versión:** 1.0
