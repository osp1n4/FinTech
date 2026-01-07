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
COPY services/api-gateway/src ./src
COPY services/shared ./shared

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
