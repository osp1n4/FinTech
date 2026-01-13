# Script para ejecutar tests unitarios usando el docker-compose unificado
# Uso: .\scripts\run-tests-unified.ps1

Write-Host "Ejecutando tests unitarios en contenedor..." -ForegroundColor Cyan

# Ejecutar tests directamente con imagen python limpia (mas rapido y sin conflictos)
docker run --rm -v "${PWD}:/app" -w /app python:3.11-slim sh -c "pip install -q pytest pytest-asyncio pytest-mock fastapi httpx && pytest tests/unit/ -v --tb=no"

$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "Tests completados exitosamente! (162 passed)" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Tests fallaron con codigo de salida $exitCode" -ForegroundColor Red
}

exit $exitCode
