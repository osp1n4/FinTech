# Script para ejecutar tests usando Docker
# Útil cuando Python no está instalado localmente

param(
    [Parameter(Mandatory=$false)]
    [switch]$Coverage,
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"

Write-Host "=== Ejecutando Tests en Docker ===" -ForegroundColor Cyan
Write-Host ""

# Verificar que Docker esté corriendo
docker ps > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker no está corriendo. Por favor inicia Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verificar que los servicios estén corriendo
Write-Host "Verificando servicios..." -ForegroundColor Yellow
$containers = docker-compose ps --services --filter "status=running"

if ($containers -notcontains "mongodb" -or $containers -notcontains "redis" -or $containers -notcontains "rabbitmq") {
    Write-Host "Levantando servicios de infraestructura..." -ForegroundColor Yellow
    docker-compose up -d mongodb redis rabbitmq
    
    Write-Host "Esperando a que los servicios estén listos..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
}

# Construir comando de pytest
$pytestCommand = "pytest tests/unit/ -v"

if ($Coverage) {
    $pytestCommand += " --cov=services --cov-report=term --cov-report=html --cov-report=xml"
}

if ($VerboseOutput) {
    $pytestCommand += " -vv"
}

# Crear contenedor temporal para ejecutar tests
Write-Host "Ejecutando tests en contenedor..." -ForegroundColor Green
Write-Host "Comando: $pytestCommand" -ForegroundColor Gray
Write-Host ""

# Ejecutar tests en un contenedor temporal
# ⚠️ Las credenciales DEBEN configurarse mediante variables de entorno
# Validar que las variables de entorno estén configuradas
if (-not $env:MONGODB_URL) {
    Write-Host "ERROR: Variable de entorno MONGODB_URL no está configurada." -ForegroundColor Red
    Write-Host "Por favor, carga el archivo .env o configura las variables manualmente." -ForegroundColor Yellow
    exit 1
}

if (-not $env:REDIS_URL) {
    Write-Host "ERROR: Variable de entorno REDIS_URL no está configurada." -ForegroundColor Red
    Write-Host "Por favor, carga el archivo .env o configura las variables manualmente." -ForegroundColor Yellow
    exit 1
}

if (-not $env:RABBITMQ_URL) {
    Write-Host "ERROR: Variable de entorno RABBITMQ_URL no está configurada." -ForegroundColor Red
    Write-Host "Por favor, carga el archivo .env o configura las variables manualmente." -ForegroundColor Yellow
    exit 1
}

$mongodbUrl = $env:MONGODB_URL
$redisUrl = $env:REDIS_URL
$rabbitmqUrl = $env:RABBITMQ_URL

docker run --rm `
    --network fraud-detection-engine_fraud-network `
    -v "${PWD}:/app" `
    -w /app `
    -e PYTHONPATH=/app `
    -e MONGODB_URL=$mongodbUrl `
    -e REDIS_URL=$redisUrl `
    -e RABBITMQ_URL=$rabbitmqUrl `
    python:3.11-slim `
    sh -c "pip install --quiet -r requirements-test.txt && $pytestCommand"

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "Tests completados exitosamente" -ForegroundColor Green
    
    if ($Coverage) {
        Write-Host ""
        Write-Host "Reporte de cobertura generado en:" -ForegroundColor Yellow
        Write-Host "  - htmlcov/index.html" -ForegroundColor Gray
        Write-Host "  - coverage.xml" -ForegroundColor Gray
    }
} else {
    Write-Host "Tests fallaron" -ForegroundColor Red
}

exit $exitCode
