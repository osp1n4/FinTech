# Script para ejecutar tests unitarios en el contenedor fraud-evaluation-service
# PowerShell version

Write-Host "Running unit tests for fraud-evaluation-service..." -ForegroundColor Cyan
Write-Host ""

# Verificar que Docker esté corriendo
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Build del servicio si no existe la imagen
Write-Host "Building fraud-evaluation-service..." -ForegroundColor Yellow
docker-compose build fraud-evaluation-service

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error building image" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host ""

# Ejecutar tests en el contenedor
# Usamos docker run directamente con la imagen construida
docker run --rm `
    -v "${PWD}/tests:/app/tests" `
    -v "${PWD}/services/fraud-evaluation-service:/app/services/fraud-evaluation-service" `
    -w /app `
    fraud-detection-engine-fraud-evaluation-service `
    pytest tests/unit/fraud_evaluation/ -v --tb=short --color=yes

$testExitCode = $LASTEXITCODE

Write-Host ""
if ($testExitCode -eq 0) {
    Write-Host "All tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed. Check output above." -ForegroundColor Red
}

exit $testExitCode
