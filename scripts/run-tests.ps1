# Script para ejecutar tests en Windows
# Este script facilita la ejecución de tests sin problemas

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('backend', 'frontend-admin', 'frontend-user', 'e2e', 'all')]
    [string]$TestType = 'all',
    
    [Parameter(Mandatory=$false)]
    [switch]$Coverage,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$rootDir = Split-Path -Parent $PSScriptRoot

Write-Host "=== Fraud Detection Engine - Test Runner ===" -ForegroundColor Cyan
Write-Host "Test Type: $TestType" -ForegroundColor Yellow
Write-Host "Coverage: $Coverage" -ForegroundColor Yellow
Write-Host ""

function Test-Backend {
    Write-Host "`n[Backend Tests] Ejecutando tests de Python..." -ForegroundColor Green
    
    # Verificar si Python está instalado
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Gray
    } catch {
        Write-Host "ERROR: Python no está instalado. Instalando dependencias via Docker..." -ForegroundColor Red
        Write-Host "Usando contenedor Docker para ejecutar tests..." -ForegroundColor Yellow
        
        # Ejecutar tests en Docker
        docker-compose exec -T api pytest /app/tests/unit/ -v
        return
    }
    
    # Instalar dependencias si no existen
    Write-Host "Verificando dependencias de pytest..." -ForegroundColor Gray
    pip show pytest > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Instalando pytest y dependencias..." -ForegroundColor Yellow
        pip install pytest pytest-asyncio pytest-cov pytest-mock
    }
    
    # Configurar PYTHONPATH
    $env:PYTHONPATH = $rootDir
    Write-Host "PYTHONPATH configurado: $env:PYTHONPATH" -ForegroundColor Gray
    
    # Ejecutar tests
    $pytestArgs = @("tests/unit/", "-v")
    
    if ($Coverage) {
        $pytestArgs += @("--cov=services", "--cov-report=xml", "--cov-report=html", "--cov-report=term")
    }
    
    if ($Verbose) {
        $pytestArgs += "-vv"
    }
    
    Push-Location $rootDir
    Write-Host "Ejecutando: pytest $($pytestArgs -join ' ')" -ForegroundColor Gray
    pytest @pytestArgs
    $backendExitCode = $LASTEXITCODE
    Pop-Location
    
    if ($backendExitCode -eq 0) {
        Write-Host "`n✓ Backend tests PASSED" -ForegroundColor Green
    } else {
        Write-Host "`n✗ Backend tests FAILED" -ForegroundColor Red
    }
    
    return $backendExitCode
}

function Test-Frontend {
    param([string]$AppName)
    
    Write-Host "`n[Frontend Tests] Ejecutando tests de $AppName..." -ForegroundColor Green
    
    $appDir = Join-Path $rootDir "frontend\$AppName"
    
    if (-not (Test-Path $appDir)) {
        Write-Host "ERROR: Directorio $appDir no existe" -ForegroundColor Red
        return 1
    }
    
    Push-Location $appDir
    
    # Verificar si node_modules existe
    if (-not (Test-Path "node_modules")) {
        Write-Host "Instalando dependencias de npm..." -ForegroundColor Yellow
        npm install
    }
    
    # Verificar si vitest está instalado
    $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
    if (-not $packageJson.devDependencies.vitest) {
        Write-Host "Instalando vitest..." -ForegroundColor Yellow
        npm install -D vitest @vitest/ui jsdom @testing-library/react @testing-library/jest-dom
    }
    
    # Ejecutar tests
    Write-Host "Ejecutando: npm test" -ForegroundColor Gray
    npm test -- --run
    $frontendExitCode = $LASTEXITCODE
    
    Pop-Location
    
    if ($frontendExitCode -eq 0) {
        Write-Host "`n✓ $AppName tests PASSED" -ForegroundColor Green
    } else {
        Write-Host "`n✗ $AppName tests FAILED" -ForegroundColor Red
    }
    
    return $frontendExitCode
}

function Test-E2E {
    Write-Host "`n[E2E Tests] Ejecutando tests end-to-end..." -ForegroundColor Green
    
    # Verificar si Docker está corriendo
    docker ps > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Docker no está corriendo" -ForegroundColor Red
        return 1
    }
    
    # Iniciar servicios
    Write-Host "Iniciando servicios con docker-compose..." -ForegroundColor Yellow
    Push-Location $rootDir
    docker-compose up -d
    Start-Sleep -Seconds 30
    
    # Ejecutar tests E2E
    Push-Location (Join-Path $rootDir "tests-e2e")
    
    if (-not (Test-Path "node_modules")) {
        Write-Host "Instalando dependencias de npm..." -ForegroundColor Yellow
        npm install
    }
    
    Write-Host "Instalando navegadores de Playwright..." -ForegroundColor Yellow
    npx playwright install --with-deps
    
    Write-Host "Ejecutando tests E2E..." -ForegroundColor Gray
    npm test
    $e2eExitCode = $LASTEXITCODE
    
    Pop-Location
    
    # Detener servicios
    Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
    docker-compose down
    
    Pop-Location
    
    if ($e2eExitCode -eq 0) {
        Write-Host "`n✓ E2E tests PASSED" -ForegroundColor Green
    } else {
        Write-Host "`n✗ E2E tests FAILED" -ForegroundColor Red
    }
    
    return $e2eExitCode
}

# Ejecutar tests según el tipo
$exitCodes = @()

switch ($TestType) {
    'backend' {
        $exitCodes += Test-Backend
    }
    'frontend-admin' {
        $exitCodes += Test-Frontend -AppName "admin-dashboard"
    }
    'frontend-user' {
        $exitCodes += Test-Frontend -AppName "user-app"
    }
    'e2e' {
        $exitCodes += Test-E2E
    }
    'all' {
        $exitCodes += Test-Backend
        $exitCodes += Test-Frontend -AppName "admin-dashboard"
        $exitCodes += Test-Frontend -AppName "user-app"
        # E2E tests son opcionales en 'all'
        Write-Host "`nNOTA: Tests E2E omitidos. Ejecutar con -TestType e2e para incluirlos." -ForegroundColor Yellow
    }
}

# Resultado final
Write-Host "`n=== Resumen de Tests ===" -ForegroundColor Cyan
$failedTests = $exitCodes | Where-Object { $_ -ne 0 }

if ($failedTests.Count -eq 0) {
    Write-Host "✓ Todos los tests pasaron exitosamente" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ $($failedTests.Count) suite(s) de tests fallaron" -ForegroundColor Red
    exit 1
}
