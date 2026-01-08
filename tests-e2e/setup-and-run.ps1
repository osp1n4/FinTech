# Instalación y Ejecución Rápida de Tests E2E

Write-Host "`n PLAYWRIGHT E2E TESTS - SETUP & RUN" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan

# Cambiar al directorio de tests
$testsDir = "c:\Users\maria.gutierrezn\Documents\fraud-detection-engine\tests-e2e"
Set-Location $testsDir

Write-Host "`n[1/4] Verificando Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($nodeVersion) {
    Write-Host "   Node.js instalado: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "   ERROR: Node.js no está instalado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n[2/4] Instalando dependencias npm..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Dependencias instaladas correctamente" -ForegroundColor Green
} else {
    Write-Host "   ERROR: Falló la instalación de dependencias" -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/4] Instalando navegadores de Playwright..." -ForegroundColor Yellow
npx playwright install
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Navegadores instalados correctamente" -ForegroundColor Green
} else {
    Write-Host "   ERROR: Falló la instalación de navegadores" -ForegroundColor Red
    exit 1
}

Write-Host "`n[4/4] Verificando servicios..." -ForegroundColor Yellow

# Verificar Backend
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    $backendRunning = $true
    Write-Host "   Backend (8000): RUNNING" -ForegroundColor Green
} catch {
    Write-Host "   Backend (8000): NOT RUNNING" -ForegroundColor Red
}

# Verificar Admin Dashboard
$adminRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    $adminRunning = $true
    Write-Host "   Admin Dashboard (3001): RUNNING" -ForegroundColor Green
} catch {
    Write-Host "   Admin Dashboard (3001): NOT RUNNING" -ForegroundColor Red
}

# Verificar User App
$userAppRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    $userAppRunning = $true
    Write-Host "   User App (5173): RUNNING" -ForegroundColor Green
} catch {
    Write-Host "   User App (5173): NOT RUNNING" -ForegroundColor Red
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " SETUP COMPLETADO" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan

if (-not $backendRunning -or -not $adminRunning -or -not $userAppRunning) {
    Write-Host "`n ADVERTENCIA: Algunos servicios no están corriendo" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para iniciar los servicios:" -ForegroundColor White
    Write-Host "  Backend:         cd services/api-gateway; poetry run uvicorn src.main:app --reload" -ForegroundColor Gray
    Write-Host "  Admin Dashboard: cd frontend/admin-dashboard; npm run dev" -ForegroundColor Gray
    Write-Host "  User App:        cd frontend/user-app; npm run dev" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "`n COMANDOS DISPONIBLES:" -ForegroundColor White
Write-Host ""
Write-Host "  npm test              # Ejecutar todos los tests" -ForegroundColor Cyan
Write-Host "  npm run test:ui       # Modo UI interactivo (RECOMENDADO)" -ForegroundColor Cyan
Write-Host "  npm run test:headed   # Ver navegador durante ejecución" -ForegroundColor Cyan
Write-Host "  npm run test:debug    # Modo debug" -ForegroundColor Cyan
Write-Host "  npm run test:report   # Ver HTML Report" -ForegroundColor Cyan
Write-Host ""
Write-Host "  npm run test:admin    # Solo tests de admin" -ForegroundColor Gray
Write-Host "  npm run test:user     # Solo tests de usuario" -ForegroundColor Gray
Write-Host "  npm run test:api      # Solo tests de API" -ForegroundColor Gray
Write-Host ""

# Preguntar si quiere ejecutar tests
Write-Host " Ejecutar tests ahora? (y/n): " -NoNewline -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "`nEjecutando tests en modo UI interactivo..." -ForegroundColor Green
    npm run test:ui
} else {
    Write-Host "`nSetup completado. Ejecuta 'npm run test:ui' cuando estés listo." -ForegroundColor Cyan
}
