#!/bin/bash
# Script para ejecutar tests unitarios en el contenedor fraud-evaluation-service

echo "🧪 Ejecutando tests unitarios de fraud-evaluation-service..."
echo ""

# Build del servicio si no existe la imagen
docker-compose build fraud-evaluation-service

# Ejecutar tests en el contenedor
docker-compose run --rm fraud-evaluation-service pytest tests/unit/fraud_evaluation/ -v --tb=short

echo ""
echo "✅ Tests completados"
