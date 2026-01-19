# Adapters - Infrastructure Layer

Este directorio contiene los adaptadores que implementan las interfaces definidas en la capa de aplicación.

## 📁 Estructura

```
adapters/
├── __init__.py              # Exporta todos los adaptadores
├── mongodb_adapter.py       # Persistencia de evaluaciones de fraude
├── redis_adapter.py         # Caché para ubicaciones y configuración
└── rabbitmq_adapter.py      # Publicación de mensajes a colas
```

## 🎯 Propósito

Cada adaptador implementa el patrón **Hexagonal Architecture (Ports & Adapters)**:
- Las interfaces (ports) están en `src.application.interfaces`
- Las implementaciones (adapters) están aquí

## 📝 Adaptadores disponibles

### MongoDBAdapter
**Implementa:** `TransactionRepository`  
**Responsabilidad:** Persistencia de evaluaciones de fraude en MongoDB  
**Uso:**
```python
from src.adapters import MongoDBAdapter

repo = MongoDBAdapter(
    connection_string="mongodb://localhost:27017",
    database_name="fraud_detection"
)
await repo.save_evaluation(evaluation)
```

### RedisAdapter
**Implementa:** `CacheService`  
**Responsabilidad:** Caché de ubicaciones de usuarios y configuración dinámica  
**Uso:**
```python
from src.adapters import RedisAdapter

cache = RedisAdapter(
    connection_string="redis://localhost:6379",
    ttl=3600
)
await cache.set_user_location(user_id, lat, lon)
```

### RabbitMQAdapter
**Implementa:** `MessagePublisher`  
**Responsabilidad:** Publicación de mensajes a colas de procesamiento  
**Uso:**
```python
from src.adapters import RabbitMQAdapter

publisher = RabbitMQAdapter(
    connection_string="amqp://localhost:5672"
)
await publisher.publish_for_manual_review(evaluation_data)
```

## ✅ Principios SOLID

### Single Responsibility (SRP)
Cada adaptador tiene **una única responsabilidad**:
- `MongoDBAdapter`: Solo persistencia
- `RedisAdapter`: Solo caché
- `RabbitMQAdapter`: Solo mensajería

### Open/Closed Principle (OCP)
Los adaptadores son **abiertos a extensión, cerrados a modificación**:
- Puedes crear `PostgreSQLAdapter` sin modificar `MongoDBAdapter`
- Puedes agregar `KafkaAdapter` sin cambiar `RabbitMQAdapter`

### Liskov Substitution (LSP)
Cualquier implementación de la interface puede ser **sustituida sin romper el código**:
```python
# Ambos funcionan porque implementan TransactionRepository
repo = MongoDBAdapter(...)
# repo = PostgreSQLAdapter(...)  # Future implementation
```

### Interface Segregation (ISP)
Cada adaptador implementa **solo la interface que necesita**:
- MongoDB no necesita implementar métodos de caché
- Redis no necesita implementar métodos de mensajería

### Dependency Inversion (DIP)
Las capas superiores dependen de **abstracciones**, no de implementaciones:
```python
# ✅ Correcto: Depender de la abstracción
def process(repo: TransactionRepository):
    ...

# ❌ Incorrecto: Depender de la implementación
def process(repo: MongoDBAdapter):
    ...
```

## 🔄 Refactorización

**Fecha:** Enero 2026  
**Por:** María Gutiérrez  
**Motivo:** Separar adaptadores en archivos individuales para mejor mantenibilidad

**Antes:**
```
src/
└── adapters.py  (320 líneas)
```

**Después:**
```
src/adapters/
├── __init__.py              (15 líneas)
├── mongodb_adapter.py       (130 líneas)
├── redis_adapter.py         (90 líneas)
└── rabbitmq_adapter.py      (100 líneas)
```

**Ventajas:**
- ✅ Mejor organización y navegación
- ✅ Menos conflictos de merge en Git
- ✅ Cumple SRP a nivel de módulo
- ✅ Más fácil de testear individualmente
- ✅ Escalable para nuevos adaptadores

## 🧪 Testing

Cada adaptador debe tener su archivo de test:
```
tests/adapters/
├── test_mongodb_adapter.py
├── test_redis_adapter.py
└── test_rabbitmq_adapter.py
```

## 📚 Referencias

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
