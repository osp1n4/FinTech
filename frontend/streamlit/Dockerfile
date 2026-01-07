FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
RUN pip install --no-cache-dir streamlit==1.30.0 requests==2.31.0

# Copiar la aplicación
COPY streamlit_app.py .

# Exponer puerto de Streamlit
EXPOSE 8501

# Comando para ejecutar
CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0"]
