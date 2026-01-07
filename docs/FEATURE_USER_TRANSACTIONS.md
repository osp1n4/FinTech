# 👤 Visualización de Transacciones por Usuario

## ✅ Cambios Implementados

Se ha agregado funcionalidad completa para visualizar las transacciones de usuarios a través del frontend Streamlit.

### 1. Backend - Nuevo Endpoint API

**Endpoint:** `GET /audit/user/{user_id}`

**Descripción:** Obtiene todas las transacciones de un usuario específico ordenadas por fecha descendente.

**Respuesta:**
```json
[
  {
    "transaction_id": "txn_20260106001",
    "user_id": "user_123",
    "risk_level": "MEDIUM_RISK",
    "risk_score": 0.65,
    "reasons": ["Amount exceeds threshold", "Unusual location"],
    "status": "PENDING_REVIEW",
    "evaluated_at": "2026-01-06T18:30:00",
    "reviewed_by": null,
    "reviewed_at": null
  }
]
```

### 2. Modelo de Datos Actualizado

Se agregó el campo `user_id` al modelo `FraudEvaluation`:

```python
@dataclass
class FraudEvaluation:
    transaction_id: str
    user_id: str  # ✅ NUEVO
    risk_level: RiskLevel
    reasons: List[str]
    timestamp: datetime
    status: str
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
```

### 3. Adaptador MongoDB

- Se agregó índice en `user_id` para mejorar el rendimiento de consultas
- Método nuevo: `get_evaluations_by_user(user_id: str)`
- El campo `user_id` se guarda automáticamente con cada evaluación

### 4. Frontend - Nueva Pestaña "Transacciones por Usuario"

**Características:**

#### 🔍 Búsqueda de Transacciones
- Campo de búsqueda por User ID
- Validación de entrada

#### 📊 Estadísticas del Usuario
Muestra métricas en tiempo real:
- 🔴 **Alto Riesgo:** Transacciones con HIGH_RISK
- 🟡 **Riesgo Medio:** Transacciones con MEDIUM_RISK
- 🟢 **Bajo Riesgo:** Transacciones con LOW_RISK
- ✅ **Aprobadas:** Transacciones con estado APPROVED

#### 📋 Historial de Transacciones
- Lista completa de todas las transacciones del usuario
- Cada transacción muestra:
  - Transaction ID
  - Nivel de riesgo con código de color
  - Score de riesgo
  - Estado actual (Aprobado/Pendiente/Rechazado)
  - Fecha de evaluación
  - Información de revisión (si aplica)
  - Razones de la evaluación
- Las primeras 3 transacciones se expanden automáticamente
- Opción para ver JSON completo de cada transacción

#### 🎨 Diseño Visual
- Iconos de colores para niveles de riesgo:
  - 🔴 Alto Riesgo
  - 🟡 Riesgo Medio
  - 🟢 Bajo Riesgo
- Estados visuales:
  - ✅ Aprobado
  - ⏳ Pendiente de Revisión
  - ❌ Rechazado

## 🚀 Cómo Usar

### 1. Iniciar los Servicios

```powershell
# Los servicios ya están corriendo en Docker
docker-compose ps
```

### 2. Instalar Streamlit (si no está instalado)

```powershell
# Opción 1: Con Poetry
poetry install --with demo

# Opción 2: Con pip
pip install streamlit requests
```

### 3. Iniciar el Frontend

```powershell
cd frontend/streamlit
streamlit run streamlit_app.py
```

El navegador se abrirá automáticamente en `http://localhost:8501`

### 4. Probar la Funcionalidad

#### Paso 1: Crear Transacciones de Prueba
1. Ve a la pestaña "📝 Evaluar Transacción"
2. Ingresa un User ID (por ejemplo: `user_test_123`)
3. Completa los demás campos
4. Haz clic en "🚀 Evaluar Transacción"
5. Repite varias veces con diferentes montos y ubicaciones

#### Paso 2: Visualizar Transacciones del Usuario
1. Ve a la pestaña "👤 Transacciones por Usuario"
2. Ingresa el User ID que usaste (`user_test_123`)
3. Haz clic en "🔎 Buscar"
4. Verás todas las transacciones del usuario con:
   - Estadísticas resumen
   - Lista detallada de transacciones
   - Posibilidad de expandir cada transacción

## 🧪 Prueba con la API Directamente

### Crear una transacción:
```powershell
$body = @{
    id = "txn_$(Get-Date -Format 'yyyyMMddHHmmss')"
    amount = 1200.0
    user_id = "user_test_123"
    location = @{
        latitude = 40.7128
        longitude = -74.0060
    }
    timestamp = (Get-Date).ToString("o")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/transaction" -Method POST -Body $body -ContentType "application/json"
```

### Consultar transacciones del usuario:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/audit/user/user_test_123" -Method GET
```

## 📊 Casos de Uso

### 1. Analista de Fraude
- Revisar el historial completo de un usuario sospechoso
- Identificar patrones de comportamiento
- Ver evolución de riesgo a lo largo del tiempo

### 2. Servicio al Cliente
- Consultar transacciones de un cliente que reporta problemas
- Verificar el estado de transacciones específicas
- Proporcionar información detallada al cliente

### 3. Compliance y Auditoría
- Generar reportes de actividad por usuario
- Revisar decisiones tomadas sobre transacciones
- Análisis de riesgo por cliente

## 🔧 Archivos Modificados

1. **services/api-gateway/src/routes.py**
   - Agregado endpoint `GET /audit/user/{user_id}`

2. **services/shared/domain/models.py**
   - Agregado campo `user_id` a `FraudEvaluation`

3. **services/shared/adapters.py**
   - Agregado método `get_evaluations_by_user()`
   - Agregado índice en `user_id`
   - Actualizado `save_evaluation()` para incluir `user_id`
   - Actualizado `_document_to_evaluation()` para mapear `user_id`

4. **services/shared/application/use_cases.py**
   - Actualizado `EvaluateTransactionUseCase.execute()` para pasar `user_id`

5. **frontend/streamlit/streamlit_app.py**
   - Agregada nueva pestaña "👤 Transacciones por Usuario"
   - Interfaz completa con búsqueda, estadísticas e historial

## ✨ Características Técnicas

- ✅ **Clean Architecture**: Separación clara de capas
- ✅ **SOLID Principles**: Código mantenible y extensible
- ✅ **Índices MongoDB**: Consultas optimizadas
- ✅ **Validación de Datos**: Control de errores robusto
- ✅ **UI/UX Mejorado**: Interfaz intuitiva y visual
- ✅ **Real-time**: Datos actualizados al momento

## 🎯 Próximos Pasos Sugeridos

1. **Filtros Avanzados**: Agregar filtros por fecha, nivel de riesgo, estado
2. **Exportación**: Permitir exportar el historial a CSV/Excel
3. **Gráficos**: Visualización de tendencias con charts
4. **Paginación**: Para usuarios con muchas transacciones
5. **WebSockets**: Actualización en tiempo real sin necesidad de refrescar

---

**Desarrollado por:** María Gutiérrez
**Fecha:** Enero 6, 2026
**Versión:** 0.2.0
