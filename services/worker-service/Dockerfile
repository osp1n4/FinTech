FROM python:3.11-slim

WORKDIR /app

# Instalar Poetry
RUN pip install poetry

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock* ./

# Configurar Poetry para no crear virtualenv
RUN poetry config virtualenvs.create false

# Instalar dependencias sin el proyecto actual
RUN poetry install --only main --no-root --no-interaction --no-ansi

# Copiar código de la aplicación
COPY services/fraud-evaluation-service/src ./src
COPY services/worker-service/src ./worker

# Comando para ejecutar el worker
CMD ["python", "-m", "worker.worker"]
