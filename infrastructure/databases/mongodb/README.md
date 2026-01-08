# MongoDB Database Configuration

Este directorio contiene scripts de inicialización para MongoDB.

## Scripts

### 01-init-db.js
- Crea la base de datos `fraud_detection`
- Crea colecciones con schemas de validación
- Crea índices para optimización de queries

## Colecciones Creadas

### fraud_evaluations
- **Propósito**: Almacenar evaluaciones de fraude
- **Índices**:
  - `transaction_id` (unique)
  - `user_id`
  - `timestamp` (descendente)
  - `status`
  - `risk_level`

### audit_logs
- **Propósito**: Registro de auditoría de acciones
- **Índices**:
  - `timestamp` (descendente)
  - `user_id`

### user_locations
- **Propósito**: Cache de ubicaciones de usuario (fallback de Redis)
- **TTL**: 24 horas
- **Índices**:
  - `user_id` (unique)
  - `updated_at` (TTL index)

## Uso en Docker

Los scripts se ejecutan automáticamente cuando el contenedor MongoDB inicia por primera vez:

```yaml
mongodb:
  volumes:
    - ./infrastructure/databases/mongodb/init-scripts:/docker-entrypoint-initdb.d
```

## Conexión

```bash
# String de conexión
mongodb://admin:fraud2026@localhost:27017

# Base de datos
fraud_detection
```
