# Fraud Evaluation Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY pyproject.toml ./

# Instalar Poetry
RUN pip install --no-cache-dir poetry

# Instalar dependencias (sin instalar el proyecto en modo paquete)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copiar código fuente
COPY src/ ./src/

# Exponer puerto 8001
EXPOSE 8001

# Comando para ejecutar el servicio
CMD ["python", "-m", "uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8001"]
