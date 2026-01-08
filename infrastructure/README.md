# Infrastructure Configuration

Este directorio contiene toda la configuración de infraestructura para el sistema de detección de fraude.

## 📁 Estructura

```
infrastructure/
├── cache/              # Redis cache configuration
│   └── redis/
│       ├── redis.conf
│       └── README.md
├── databases/          # Database initialization scripts
│   └── mongodb/
│       ├── init-scripts/
│       │   └── 01-init-db.js
│       └── README.md
└── messaging/          # Message broker configuration
    └── rabbitmq/
        ├── definitions.json
        └── README.md
```

## 🎯 Propósito

Centralizar toda la configuración de infraestructura para:
1. **Reproducibilidad**: Mismo setup en dev, staging, producción
2. **Documentación**: Cada componente está documentado
3. **Versionamiento**: Configuración bajo control de versiones
4. **Automatización**: Scripts de inicialización automáticos

## 🚀 Uso con Docker Compose

Los archivos de configuración se montan como volúmenes en los contenedores:

```yaml
# MongoDB con script de inicialización
mongodb:
  volumes:
    - ./infrastructure/databases/mongodb/init-scripts:/docker-entrypoint-initdb.d:ro

# Redis con configuración personalizada
redis:
  command: redis-server /usr/local/etc/redis/redis.conf
  volumes:
    - ./infrastructure/cache/redis/redis.conf:/usr/local/etc/redis/redis.conf:ro

# RabbitMQ con definiciones precargadas
rabbitmq:
  environment:
    RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS: -rabbitmq_management load_definitions "/etc/rabbitmq/definitions.json"
  volumes:
    - ./infrastructure/messaging/rabbitmq/definitions.json:/etc/rabbitmq/definitions.json:ro
```

## 📦 Componentes

### 1. Cache (Redis)
- **Propósito**: Cache de alta velocidad para ubicaciones, sesiones, configuración
- **Puerto**: 6379
- **Configuración**: [cache/redis/README.md](cache/redis/README.md)

### 2. Databases (MongoDB)
- **Propósito**: Almacenamiento persistente de evaluaciones de fraude
- **Puerto**: 27017
- **Script de inicialización**: Crea colecciones con schemas e índices
- **Configuración**: [databases/mongodb/README.md](databases/mongodb/README.md)

### 3. Messaging (RabbitMQ)
- **Propósito**: Cola de mensajes para procesamiento asíncrono
- **Puertos**: 5672 (AMQP), 15672 (Management UI)
- **Queues**: transactions, manual_review, notifications, dead_letter
- **Configuración**: [messaging/rabbitmq/README.md](messaging/rabbitmq/README.md)

## 🔧 Inicialización

### Primer arranque
```bash
# Iniciar todos los servicios con infraestructura
docker-compose up -d mongodb redis rabbitmq

# Verificar que la inicialización fue exitosa
docker logs fraud-mongodb    # Ver script de MongoDB
docker exec -it fraud-rabbitmq rabbitmqctl list_queues
docker exec -it fraud-redis redis-cli INFO
```

### Verificación de health checks
```bash
# Ver estado de servicios
docker-compose ps

# Debe mostrar "healthy" para mongodb, redis, rabbitmq
```

## 🔍 Monitoreo

### MongoDB
```bash
# Conectar al shell
docker exec -it fraud-mongodb mongosh -u admin -p fraud2026

# Ver colecciones
use fraud_detection
show collections
```

### Redis
```bash
# Conectar al CLI
docker exec -it fraud-redis redis-cli

# Ver estadísticas
INFO stats
INFO memory
```

### RabbitMQ
- **Management UI**: http://localhost:15672
- **Credenciales**: fraud / fraud2026
- Ver queues, exchanges, bindings en la interfaz web

## ⚠️ Seguridad (Producción)

**IMPORTANTE**: En producción DEBES:

1. **Cambiar todas las contraseñas** en [docker-compose.yml](../docker-compose.yml)
   ```yaml
   MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
   RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
   ```

2. **Usar variables de entorno** (archivo `.env`):
   ```env
   MONGODB_PASSWORD=secure_random_password_here
   RABBITMQ_PASSWORD=another_secure_password
   REDIS_PASSWORD=yet_another_secure_password
   ```

3. **Habilitar requirepass en Redis** (redis.conf):
   ```conf
   requirepass ${REDIS_PASSWORD}
   ```

4. **Limitar acceso por IP** en todos los servicios:
   ```conf
   bind 10.0.1.0/24
   ```

5. **Usar TLS/SSL** para todas las conexiones:
   - MongoDB: `mongodb+srv://` con certificados
   - Redis: `rediss://` con TLS habilitado
   - RabbitMQ: `amqps://` con certificados

## 🧪 Testing

### Probar conectividad desde servicios Python
```python
# Test MongoDB
from pymongo import MongoClient
client = MongoClient("mongodb://admin:fraud2026@localhost:27017")
print(client.list_database_names())

# Test Redis
import redis
r = redis.from_url("redis://localhost:6379")
r.set("test", "hello")
print(r.get("test"))

# Test RabbitMQ
import pika
connection = pika.BlockingConnection(
    pika.URLParameters("amqp://fraud:fraud2026@localhost:5672")
)
channel = connection.channel()
print("RabbitMQ connected!")
```

## 🔄 Backup y Restore

### MongoDB
```bash
# Backup
docker exec fraud-mongodb mongodump --out /backup

# Restore
docker exec fraud-mongodb mongorestore /backup
```

### Redis
```bash
# Backup (crea dump.rdb)
docker exec fraud-redis redis-cli BGSAVE

# Backup inmediato
docker exec fraud-redis redis-cli SAVE

# Backup está en /data/dump.rdb dentro del contenedor
```

### RabbitMQ
```bash
# Export definitions
curl -u fraud:fraud2026 http://localhost:15672/api/definitions > backup.json

# Import definitions
curl -u fraud:fraud2026 -X POST -H "Content-Type: application/json" \
  --data @backup.json http://localhost:15672/api/definitions
```

## 📚 Referencias

- [MongoDB Docker Hub](https://hub.docker.com/_/mongo)
- [Redis Docker Hub](https://hub.docker.com/_/redis)
- [RabbitMQ Docker Hub](https://hub.docker.com/_/rabbitmq)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Contribuir

Al agregar nuevos componentes de infraestructura:
1. Crear carpeta en `infrastructure/`
2. Agregar archivos de configuración
3. Crear README.md explicando el componente
4. Actualizar este README con el nuevo componente
5. Agregar volumen en docker-compose.yml
