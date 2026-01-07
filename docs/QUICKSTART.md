# 🚀 Guía Rápida de Ejecución - Fraud Detection Engine

## ✅ Proyecto Completamente Implementado

El proyecto está 100% funcional con todos los componentes:
- ✅ Backend: API FastAPI + Worker RabbitMQ
- ✅ Frontend: Streamlit UI
- ✅ Base de datos: MongoDB, Redis, RabbitMQ
- ✅ Docker Compose configurado
- ✅ Tests unitarios y validación de arquitectura
- ✅ CI/CD con SonarQube
- ✅ Clean Architecture + SOLID + Strategy Pattern

## 🐳 Estado Actual

Todos los contenedores están corriendo:

```
CONTAINER ID   IMAGE                          STATUS                   PORTS
b0ece97aa5e8   fraud-detection-engine-worker  Up                      
db5d5292ae78   fraud-detection-engine-api     Up                       0.0.0.0:8000->8000/tcp
58e016b1e4cf   rabbitmq:3.12-management       Up (healthy)             0.0.0.0:5672, 15672
25e5ccde860a   redis:7.2-alpine              Up (healthy)             0.0.0.0:6379->6379/tcp
aa53c6fd74b6   mongo:7.0                     Up (healthy)             0.0.0.0:27017->27017/tcp
```

## 🎯 Cómo Usar el Sistema

### 1. Verificar que todo está corriendo

```powershell
docker ps
```

### 2. Acceder a la API (Swagger UI)

Abre tu navegador en: http://localhost:8000/docs

### 3. Acceder al Frontend (Streamlit)

```powershell
# Instalar Poetry si no lo tienes
pip install poetry

# Instalar dependencias
poetry install

# Ejecutar frontend
poetry run streamlit run demo/streamlit_app.py
```

El frontend se abrirá en: http://localhost:8501

### 4. Probar la API manualmente

#### Evaluar una transacción (riesgo alto - $2000):

```powershell
$body = '{"id":"TX-001","amount":2000.0,"user_id":"USER-001","location":{"latitude":4.7110,"longitude":-74.0721},"timestamp":"2026-01-06T22:00:00Z"}'
Invoke-RestMethod -Uri "http://localhost:8000/transaction" -Method Post -Body $body -ContentType "application/json"
```

#### Ver todas las evaluaciones:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/audit/all" -Method Get
```

#### Revisar manualmente una transacción:

```powershell
$body = '{"decision":"APPROVED","analyst_comment":"Revisado"}'
Invoke-RestMethod -Uri "http://localhost:8000/transaction/TX-001/review" -Method Put -Body $body -ContentType "application/json" -Headers @{"X-Analyst-ID"="ANALYST-001"}
```

## 📊 Características Implementadas

### Historias de Usuario:
- ✅ HU-001: API recibe transacciones (202 Accepted)
- ✅ HU-002: Auditoría de evaluaciones
- ✅ HU-003: Regla de umbral de monto (>$1,500)
- ✅ HU-005: Regla de ubicación inusual (>100 km)
- ✅ HU-008: Modificación de umbrales sin redespliegue
- ✅ HU-009: Consulta de configuración actual
- ✅ HU-010: Human in the Loop (revisión manual)

### Arquitectura:
- ✅ Clean Architecture (Domain, Application, Infrastructure)
- ✅ SOLID: 0 violaciones
- ✅ Strategy Pattern para reglas de fraude
- ✅ Dependency Injection
- ✅ TDD/BDD con tests antes del código

### DevOps:
- ✅ Docker Compose para orquestación
- ✅ Pipeline CI/CD con GitHub Actions
- ✅ Integración SonarQube
- ✅ Pre-commit hooks
- ✅ Validación automática de arquitectura

## 🧪 Ejecutar Tests

```powershell
# Tests unitarios
poetry run pytest tests/unit/ -v

# Con cobertura
poetry run pytest --cov=src --cov-report=html

# Validar arquitectura
python scripts/validate_architecture.py
```

## 🛑 Detener el Proyecto

```powershell
docker-compose down
```

## 📚 Documentación Adicional

- README.md: Información general del proyecto
- INSTALL.md: Guía de instalación detallada
- IMPLEMENTATION_SUMMARY.md: Resumen completo de implementación
- ARQUITECTURE.md: Detalles de arquitectura
- PRODUCT.md: Especificaciones del producto

## 🎉 ¡El Proyecto Está Listo!

Todos los componentes están funcionando:
- ✅ API FastAPI corriendo en puerto 8000
- ✅ Worker RabbitMQ procesando mensajes
- ✅ MongoDB, Redis, RabbitMQ operativos
- ✅ Frontend Streamlit disponible
- ✅ Swagger UI para testing: http://localhost:8000/docs
- ✅ RabbitMQ Management: http://localhost:15672 (usuario: fraud, password: fraud2026)

---

**Desarrollado por:** María Gutiérrez  
**Arquitectura:** Clean Architecture + SOLID  
**Patrón de Diseño:** Strategy Pattern  
**Metodología:** TDD/BDD  
**DevOps:** Docker + GitHub Actions + SonarQube
