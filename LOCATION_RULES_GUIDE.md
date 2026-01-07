# 📍 Guía de Reglas de Ubicación

## 🎯 Objetivo
Detectar fraudes cuando una transacción se realiza desde una ubicación inusual (fuera del radio habitual del usuario).

## ⚙️ Configuración Actual

```yaml
Radio Permitido: 100 km
Fórmula: Haversine (distancia geodésica real)
Almacenamiento: Redis (cache)
TTL en Redis: 24 horas (86400 segundos)
```

## 🔄 Flujo de Funcionamiento

### Primera Transacción (Usuario Nuevo)
```
Usuario: user_location_demo
Transacción 1: Nueva York (40.7128, -74.0060)
                    ↓
         ┌──────────────────────┐
         │ ¿Hay historial?      │
         │ NO (primera vez)     │
         └──────────────────────┘
                    ↓
         ┌──────────────────────┐
         │ Risk: LOW_RISK       │
         │ Reason: no_historical│
         │        _location     │
         └──────────────────────┘
                    ↓
    Redis: user:user_location_demo:location
           {"latitude": 40.7128, "longitude": -74.006}
```

### Segunda Transacción (Dentro del Radio)
```
Transacción 2: Brooklyn (40.6782, -73.9442)
                    ↓
         ┌──────────────────────┐
         │ Redis tiene:         │
         │ NY (40.7128,-74.006) │
         └──────────────────────┘
                    ↓
         ┌──────────────────────┐
         │ Calcular Haversine:  │
         │ Distancia ≈ 7.5 km   │
         └──────────────────────┘
                    ↓
         ┌──────────────────────┐
         │ 7.5 km < 100 km?     │
         │ SÍ → LOW_RISK        │
         └──────────────────────┘
                    ↓
    Actualiza Redis con nueva ubicación
```

### Tercera Transacción (Fuera del Radio)
```
Transacción 3: Miami (25.7617, -80.1918)
                    ↓
         ┌──────────────────────┐
         │ Redis tiene:         │
         │ Brooklyn (40.6782,   │
         │          -73.9442)   │
         └──────────────────────┘
                    ↓
         ┌──────────────────────┐
         │ Calcular Haversine:  │
         │ Distancia ≈ 1760 km  │
         └──────────────────────┘
                    ↓
         ┌──────────────────────┐
         │ 1760 km > 100 km?    │
         │ SÍ → HIGH_RISK ⚠️    │
         │ Status: PENDING_     │
         │         REVIEW       │
         └──────────────────────┘
                    ↓
    Enviado a cola RabbitMQ para revisión manual
```

## 📊 Resultados de Pruebas Reales

| Transacción | Origen → Destino | Distancia | Resultado | Razón |
|-------------|------------------|-----------|-----------|-------|
| txn_loc_001 | (primera) → Nueva York | N/A | ✅ LOW_RISK | no_historical_location |
| txn_loc_002 | Nueva York → Brooklyn | ~7.5 km | ✅ LOW_RISK | Dentro del radio |
| txn_loc_003 | Brooklyn → Miami | ~1,760 km | ⚠️ HIGH_RISK | unusual_location |
| txn_loc_004 | Miami → Londres | ~7,100 km | ⚠️ HIGH_RISK | unusual_location |

## 🧮 Fórmula de Haversine

```python
def _calculate_distance(loc1, loc2):
    """
    Calcula distancia entre dos puntos en la Tierra
    
    Fórmula:
    a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
    c = 2 × atan2(√a, √(1−a))
    d = R × c
    
    Donde R = 6371 km (radio terrestre)
    """
    earth_radius_km = 6371.0
    
    # Convertir a radianes
    lat1, lon1 = radians(loc1.latitude), radians(loc1.longitude)
    lat2, lon2 = radians(loc2.latitude), radians(loc2.longitude)
    
    # Diferencias
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    return earth_radius_km * c
```

## 🔍 Cómo Validar las Reglas

### 1. Verificar ubicación guardada en Redis
```powershell
docker exec fraud-redis redis-cli GET "user:{user_id}:location"
```

**Ejemplo:**
```powershell
docker exec fraud-redis redis-cli GET "user:user_location_demo:location"
# Output: {"latitude": 40.7128, "longitude": -74.006}
```

### 2. Ver todas las ubicaciones guardadas
```powershell
docker exec fraud-redis redis-cli KEYS "user:*:location"
```

### 3. Crear transacción de prueba
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/transaction' `
  -Method POST `
  -ContentType 'application/json' `
  -Body '{
    "id": "txn_test",
    "amount": 500,
    "user_id": "user_test",
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }'
```

### 4. Consultar historial del usuario
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/audit/user/user_test' -Method GET
```

## 🌍 Ciudades de Referencia para Pruebas

```yaml
# Distancias desde Nueva York (40.7128, -74.0060):
Brooklyn:        (40.6782, -73.9442)  # ~7.5 km    ✅ LOW_RISK
Philadelphia:    (39.9526, -75.1652)  # ~130 km   ⚠️ HIGH_RISK
Boston:          (42.3601, -71.0589)  # ~306 km   ⚠️ HIGH_RISK
Washington DC:   (38.9072, -77.0369)  # ~328 km   ⚠️ HIGH_RISK
Miami:           (25.7617, -80.1918)  # ~1,760 km ⚠️ HIGH_RISK
Los Angeles:     (34.0522, -118.2437) # ~3,944 km ⚠️ HIGH_RISK
Londres:         (51.5074, -0.1278)   # ~5,570 km ⚠️ HIGH_RISK
Tokio:           (35.6762, 139.6503)  # ~10,850 km ⚠️ HIGH_RISK
```

## 🎨 Escenarios de Prueba

### Escenario 1: Usuario viajando gradualmente
```powershell
# 1. Primera transacción en Nueva York
Invoke-RestMethod -Uri 'http://localhost:8000/transaction' -Method POST -Body '{...NY...}'
# Resultado: LOW_RISK (no_historical_location)

# 2. Segunda en Brooklyn (7.5 km)
Invoke-RestMethod -Uri 'http://localhost:8000/transaction' -Method POST -Body '{...Brooklyn...}'
# Resultado: LOW_RISK (dentro del radio)

# 3. Tercera en Filadelfia (desde Brooklyn: 130 km)
Invoke-RestMethod -Uri 'http://localhost:8000/transaction' -Method POST -Body '{...Philly...}'
# Resultado: HIGH_RISK (fuera del radio)
```

### Escenario 2: Fraude detectado
```powershell
# Usuario hace transacción en NY
# 5 minutos después hace transacción en Londres (5,570 km)
# Sistema detecta: HIGH_RISK - unusual_location
# Enviado automáticamente a revisión manual
```

## ⚙️ Ajustar la Configuración

### Cambiar el radio permitido
```powershell
# Opción 1: Variable de entorno (requiere reinicio)
$env:LOCATION_RADIUS_KM = "200"
docker-compose restart api worker

# Opción 2: Endpoint de configuración
Invoke-RestMethod -Uri 'http://localhost:8000/config/thresholds' `
  -Method PUT `
  -ContentType 'application/json' `
  -Body '{"amount_threshold": 1500, "location_radius_km": 200}'
```

### Verificar configuración actual
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/config/thresholds' -Method GET
```

## 🧪 Script de Validación Completa

```powershell
# Script para validar reglas de ubicación
$userId = "user_validation_test"

Write-Host "1. Transacción inicial (Nueva York)" -ForegroundColor Cyan
Invoke-RestMethod -Uri 'http://localhost:8000/transaction' -Method POST -Body @"
{
  "id": "txn_val_01",
  "amount": 500,
  "user_id": "$userId",
  "location": {"latitude": 40.7128, "longitude": -74.0060}
}
"@

Write-Host "`n2. Verificando Redis..." -ForegroundColor Yellow
docker exec fraud-redis redis-cli GET "user:$userId:location"

Write-Host "`n3. Transacción cercana (Brooklyn)" -ForegroundColor Cyan
Invoke-RestMethod -Uri 'http://localhost:8000/transaction' -Method POST -Body @"
{
  "id": "txn_val_02",
  "amount": 500,
  "user_id": "$userId",
  "location": {"latitude": 40.6782, "longitude": -73.9442}
}
"@

Write-Host "`n4. Transacción lejana (Miami)" -ForegroundColor Cyan
Invoke-RestMethod -Uri 'http://localhost:8000/transaction' -Method POST -Body @"
{
  "id": "txn_val_03",
  "amount": 500,
  "user_id": "$userId",
  "location": {"latitude": 25.7617, "longitude": -80.1918}
}
"@

Write-Host "`n5. Resumen de evaluaciones:" -ForegroundColor Green
Invoke-RestMethod -Uri "http://localhost:8000/audit/user/$userId" -Method GET
```

## 📝 Notas Importantes

1. **Primera transacción siempre es LOW_RISK**: No hay ubicación histórica para comparar
2. **Redis actualiza con cada transacción**: La última ubicación siempre se guarda
3. **TTL de 24 horas**: Si no hay transacciones en 24h, la ubicación expira
4. **Distancia geodésica real**: Usa Haversine, no distancia lineal
5. **HIGH_RISK va a revisión manual**: Status automático es PENDING_REVIEW

## 🔗 Referencias

- **Código**: `services/shared/domain/strategies/location_check.py`
- **Cache**: `services/shared/adapters.py` (RedisAdapter)
- **Config**: `services/shared/config.py` (location_radius_km)
- **Haversine**: [Wikipedia](https://en.wikipedia.org/wiki/Haversine_formula)
