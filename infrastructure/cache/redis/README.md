# Redis Cache Configuration

Este directorio contiene configuración para Redis como capa de caché.

## Propósito

Redis se usa para:
1. **Cache de ubicaciones de usuario** - Historial reciente para detección de fraude
2. **Cache de configuración** - Umbrales dinámicos sin redespliegue
3. **Sesiones de usuario** - Datos de sesión efímeros
4. **Cache de dispositivos conocidos** - Validación rápida de dispositivos

## Estructura de Claves

### Convención de Nombres

```
location:{user_id}          → {"latitude": 40.7128, "longitude": -74.0060}
config:thresholds           → {"amount_threshold": 1500.0, "location_radius_km": 100.0}
session:{user_id}           → {"token": "...", "expires_at": "..."}
device:{device_id}          → {"user_id": "user_001", "registered_at": "..."}
```

### TTL por Tipo de Clave

| Tipo | TTL | Razón |
|------|-----|-------|
| `location:*` | 24 horas | Ubicaciones cambian frecuentemente |
| `config:*` | Sin expiración | Invalidación manual |
| `session:*` | 1 hora | Sesiones de corta duración |
| `device:*` | 7 días | Dispositivos son relativamente estables |

## Configuración

### Persistencia
- **RDB Snapshots**: Cada 15min si hay cambios
- **AOF (Append Only File)**: Activado, fsync cada segundo
- **Ventaja**: Balance entre rendimiento y durabilidad

### Memoria
- **Max Memory**: 256 MB
- **Eviction Policy**: `allkeys-lru` (Least Recently Used)
- **Razón**: Si la memoria se llena, elimina las claves menos usadas

### Notificaciones
- **Keyspace Events**: `Ex` (eventos de expiración)
- **Uso**: Detectar cuando una ubicación expira para limpiar datos relacionados

## Uso en Docker

```yaml
redis:
  image: redis:7-alpine
  volumes:
    - ./infrastructure/cache/redis/redis.conf:/usr/local/etc/redis/redis.conf
    - redis_data:/data
  command: redis-server /usr/local/etc/redis/redis.conf
```

## Comandos Útiles

### Conectar al CLI
```bash
docker exec -it fraud-redis redis-cli
```

### Ver estadísticas
```bash
INFO stats
INFO memory
```

### Listar claves por patrón
```bash
KEYS location:*
KEYS config:*
```

### Ver TTL de una clave
```bash
TTL location:user_001
```

### Ver todas las claves (cuidado en producción)
```bash
SCAN 0 COUNT 100
```

## Ejemplos de Uso

### Python (redis-py)
```python
import redis

# Conectar
r = redis.from_url('redis://localhost:6379')

# Set con TTL
r.setex('location:user_001', 86400, '{"latitude": 40.7128, "longitude": -74.0060}')

# Get
location = r.get('location:user_001')

# Set sin expiración
r.set('config:thresholds', '{"amount_threshold": 1500.0}')
```

### Verificar Conexión
```python
import redis.asyncio as redis_async

async def test_redis():
    client = await redis_async.from_url('redis://localhost:6379')
    await client.set('test', 'hello')
    value = await client.get('test')
    print(value)  # b'hello'
    await client.delete('test')
    await client.close()
```

## Monitoreo

### Ver comandos en tiempo real
```bash
docker exec -it fraud-redis redis-cli MONITOR
```

### Slow queries
```bash
docker exec -it fraud-redis redis-cli SLOWLOG GET 10
```

### Latency
```bash
docker exec -it fraud-redis redis-cli LATENCY DOCTOR
```

## High Availability (Futuro)

Para producción se recomienda:
1. **Redis Sentinel** - Failover automático
2. **Redis Cluster** - Sharding y réplicas
3. **Réplicas** - Al menos 1 réplica por nodo

Ejemplo de sentinel:
```conf
# sentinel.conf
sentinel monitor mymaster redis 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 10000
```

## Seguridad (Producción)

**IMPORTANTE**: En producción:
1. Habilitar `requirepass` en redis.conf
2. Usar TLS/SSL para conexiones
3. Limitar `bind` a IPs específicas
4. Usar Redis ACL (Access Control Lists)

```conf
# Ejemplo producción
requirepass your_secure_password_here
bind 10.0.1.0/24
```

## Backup

### Manual
```bash
docker exec fraud-redis redis-cli BGSAVE
```

### Automático
Los snapshots RDB se guardan automáticamente según configuración `save` en redis.conf.

### Restaurar
1. Copiar `dump.rdb` a `/data`
2. Reiniciar contenedor
