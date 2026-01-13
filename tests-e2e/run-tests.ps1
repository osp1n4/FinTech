# Script para ejecutar tests E2E de Playwright
# Verifica que los servicios estén corriendo antes de ejecutar

Write-Host "🚀 Iniciando Tests E2E de Playwright..." -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que Docker esté corriendo
Write-Host "📦 Verificando servicios Docker..." -ForegroundColor Yellow
$null = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker no está corriendo. Iniciando servicios..." -ForegroundColor Red
    docker-compose up -d
    Start-Sleep -Seconds 10
}

# 2. Verificar que el API esté respondiendo
Write-Host "🔍 Verificando API en http://localhost:8000..." -ForegroundColor Yellow
$apiHealthy = $false
$maxRetries = 10
$retryCount = 0

while (-not $apiHealthy -and $retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $apiHealthy = $true
            Write-Host "✅ API está respondiendo correctamente" -ForegroundColor Green
        }
    } catch {
        $retryCount++
        Write-Host "⏳ Esperando API... intento $retryCount/$maxRetries" -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
}

if (-not $apiHealthy) {
    Write-Host "❌ El API no está disponible después de $maxRetries intentos" -ForegroundColor Red
    Write-Host "💡 Verifica que docker-compose esté corriendo: docker-compose ps" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 3. Ejecutar tests de Playwright
Write-Host "🧪 Ejecutando tests de Playwright..." -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# Configurar variables de entorno
$env:API_URL = "http://localhost:8000"
$env:USER_APP_URL = "http://localhost:5173"
$env:ADMIN_URL = "http://localhost:5174"

# Ejecutar tests
npx playwright test --reporter=list,html

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ Todos los tests pasaron exitosamente!" -ForegroundColor Green
} else {
    Write-Host "❌ Algunos tests fallaron. Revisa el reporte en test-results/html-report/index.html" -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Para ver el reporte HTML ejecuta: npx playwright show-report" -ForegroundColor Cyan

exit $exitCode
