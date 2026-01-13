# 🔐 Guía de Configuración de Seguridad

## ⚠️ IMPORTANTE: Gestión de Credenciales

Este documento describe las mejoras de seguridad implementadas para el proyecto FinTech Fraud Detection Engine.

---

## 📋 Resumen de Cambios

### ✅ Issues de Seguridad Corregidos

1. **Contraseñas hardcodeadas eliminadas** - Todas las contraseñas se gestionan ahora mediante variables de entorno
2. **GitHub Actions asegurado** - Las credenciales se manejan mediante GitHub Secrets
3. **Docker Compose asegurado** - Uso de variables de entorno con validación
4. **Configuración refactorizada** - Los archivos de configuración ya no contienen valores por defecto inseguros

---

## 🚀 Configuración para Desarrollo Local

### 1. Crear archivo .env

Copia el archivo `.env.local.example` a `.env` en la raíz del proyecto:

```bash
cp .env.local.example .env
```

### 2. Configurar credenciales

Edita el archivo `.env` y cambia las contraseñas:

```env
# MongoDB Configuration
MONGODB_USERNAME=admin
MONGODB_PASSWORD=tu_password_seguro_aqui
MONGODB_URL=mongodb://admin:tu_password_seguro_aqui@mongodb:27017

# RabbitMQ Configuration
RABBITMQ_USERNAME=fraud
RABBITMQ_PASSWORD=tu_password_seguro_aqui
RABBITMQ_URL=amqp://fraud:tu_password_seguro_aqui@rabbitmq:5672
```

### 3. Levantar servicios

```bash
docker-compose up -d
```

---

## 🏢 Configuración para Producción

### Opción 1: Variables de Entorno del Sistema

```bash
export MONGODB_USERNAME="admin"
export MONGODB_PASSWORD="password_super_seguro"
export MONGODB_URL="mongodb://admin:password_super_seguro@mongodb.prod:27017"
export RABBITMQ_USERNAME="fraud"
export RABBITMQ_PASSWORD="password_super_seguro"
export RABBITMQ_URL="amqp://fraud:password_super_seguro@rabbitmq.prod:5672"
```

### Opción 2: Docker Secrets (Recomendado para Docker Swarm)

```bash
# Crear secrets
echo "password_super_seguro" | docker secret create mongodb_password -
echo "password_super_seguro" | docker secret create rabbitmq_password -

# Usar en docker-compose.yml
version: '3.8'
services:
  mongodb:
    secrets:
      - mongodb_password
    environment:
      MONGO_INITDB_ROOT_PASSWORD_FILE: /run/secrets/mongodb_password

secrets:
  mongodb_password:
    external: true
  rabbitmq_password:
    external: true
```

### Opción 3: Azure Key Vault (Recomendado para Azure)

```python
# En config.py
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net", credential=credential)

mongodb_password = client.get_secret("mongodb-password").value
rabbitmq_password = client.get_secret("rabbitmq-password").value
```

---

## 🔧 GitHub Actions

### Configurar Secrets

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Agrega los siguientes secrets:

```
MONGODB_TEST_PASSWORD=password_para_tests
RABBITMQ_TEST_PASSWORD=password_para_tests
SONAR_TOKEN=tu_token_de_sonarqube
SONAR_HOST_URL=https://tu-sonarqube.com
```

Los workflows ahora usan estos secrets automáticamente.

---

## 📝 Archivos Modificados

### Backend

- ✅ `services/api-gateway/src/config.py` - Credenciales requeridas sin valores por defecto
- ✅ `services/fraud-evaluation-service/src/config.py` - Credenciales requeridas sin valores por defecto
- ✅ `services/api-gateway/src/routes.py` - Refactorizado para reducir complejidad

### DevOps

- ✅ `docker-compose.yml` - Variables de entorno con validación
- ✅ `.github/workflows/ci.yml` - Uso de GitHub Secrets
- ✅ `scripts/run-tests-docker.ps1` - Variables de entorno sanitizadas

### Configuración

- ✅ `.env.example` - Plantilla con advertencias de seguridad
- ✅ `.env.local.example` - Ejemplo para desarrollo local

---

## 🛡️ Mejores Prácticas

### ✓ DO (Hacer)

- ✅ Usar gestores de secretos (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault)
- ✅ Rotar contraseñas regularmente
- ✅ Usar contraseñas únicas por ambiente (dev, staging, prod)
- ✅ Validar que las variables de entorno estén configuradas al iniciar
- ✅ Usar Docker Secrets en producción
- ✅ Añadir `.env` a `.gitignore`

### ✗ DON'T (No hacer)

- ❌ Nunca commitear credenciales al repositorio
- ❌ No usar contraseñas por defecto en producción
- ❌ No compartir credenciales por chat o email
- ❌ No usar la misma contraseña en múltiples ambientes
- ❌ No loguear credenciales en la aplicación

---

## 🧪 Testing

Para ejecutar tests localmente:

```bash
# Asegúrate de tener el archivo .env configurado
docker-compose up -d mongodb redis rabbitmq

# Ejecutar tests
poetry run pytest tests/unit/ -v
```

---

## 📊 Verificación de SonarQube

Todos los issues de seguridad Blocker han sido resueltos:

- ✅ Contraseñas hardcodeadas eliminadas (8 issues)
- ✅ Inyección de código en GitHub Actions prevenida (1 issue)
- ✅ Complejidad cognitiva reducida (3 issues)
- ✅ Code smells corregidos (27 issues)

---

## 📞 Soporte

Si tienes preguntas sobre la configuración de seguridad:

1. Revisa esta documentación
2. Consulta `.env.example` para ver todas las variables requeridas
3. Contacta al equipo DevOps

---

## 🔄 Changelog

### v2.0.0 (2026-01-12)

- **BREAKING**: Eliminadas contraseñas por defecto en archivos de configuración
- **BREAKING**: Variables `MONGODB_URL` y `RABBITMQ_URL` ahora son requeridas
- Agregado soporte para variables de entorno en Docker Compose
- Agregado soporte para GitHub Secrets en CI/CD
- Refactorizado código backend para reducir complejidad
- Corregidos todos los issues de SonarQube

---

**Nota**: Este documento debe mantenerse actualizado cuando se agreguen nuevas credenciales o servicios.
