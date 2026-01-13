# Docker Compose Unificado - Guía de Uso

## 📋 Descripción
El archivo `docker-compose.yml` ahora está unificado y sirve tanto para desarrollo como para testing.

## 🚀 Comandos principales

### Iniciar servicios (desarrollo/producción)
```bash
docker-compose up -d --build
```

### Detener servicios
```bash
docker-compose down
```

### Ver estado de servicios
```bash
docker-compose ps
```

## 🧪 Ejecutar tests

### Opción 1: Usar el script de PowerShell (recomendado)
```powershell
.\scripts\run-tests-unified.ps1
```

### Opción 2: Comando directo con docker
```bash
docker run --rm -v "${PWD}:/app" -w /app python:3.11-slim sh -c "pip install -q pytest pytest-asyncio pytest-mock fastapi httpx && pytest tests/unit/ -v"
```

### Opción 3: Usar el servicio api del docker-compose
```bash
docker-compose run --rm api pytest tests/unit/ -v
```
*(Nota: Puede requerir instalar dependencias de test primero)*

## 📦 Servicios disponibles

- **mongodb**: Base de datos (puerto 27017)
- **redis**: Cache (puerto 6379)  
- **rabbitmq**: Message broker (puerto 5672, UI en 15672)
- **api**: API Gateway (puerto 8000)
- **worker**: Worker service (sin puerto expuesto)
- **frontend-user**: Aplicación de usuario (puerto 3000)
- **frontend-admin**: Dashboard admin (puerto 3001)

## 🔧 Volúmenes incluidos para testing

Los servicios `api` y `worker` ahora tienen montados:
- Código fuente (`./services`)
- Tests (`./tests`)
- Configuración de pytest (`pytest.ini`)
- Dependencias de test (`requirements-test.txt`)

## ✅ Resultado esperado de tests
```
============================= 162 passed in ~6s ==============================
```

## 📝 Notas
- Ya no necesitas `docker-compose.test.yml` (puedes eliminarlo)
- Los volúmenes permiten hot-reload durante desarrollo
- Las variables de entorno incluyen `PYTHONPATH=/app` para imports correctos
