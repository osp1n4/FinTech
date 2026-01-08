#!/usr/bin/env pwsh
# Script para iniciar todos los servicios del proyecto
# Autor: Fraud Detection Engine Team
# Fecha: 2026-01-08

Write-Host "`n🚀 INICIANDO FRAUD DETECTION ENGINE" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$rootPath = "C:\Users\maria.gutierrezn\Documents\fraud-detection-engine"

# Verificar que Python esté instalado
Write-Host "[1/4] Verificando Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ Python no encontrado. Por favor instala Python 3.11+" -ForegroundColor Red
    Write-Host "   Descarga: https://www.python.org/downloads/" -ForegroundColor Cyan
    exit 1
}
$pythonVersion = & python --version
Write-Host "✅ $pythonVersion encontrado" -ForegroundColor Green

# Verificar que Poetry esté instalado
Write-Host "`n[2/4] Verificando Poetry..." -ForegroundColor Yellow
$poetryCmd = Get-Command poetry -ErrorAction SilentlyContinue
if (-not $poetryCmd) {
    Write-Host "⚙️  Poetry no encontrado. Instalando..." -ForegroundColor Yellow
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    
    # Agregar Poetry al PATH para esta sesión
    $poetryPath = "$env:APPDATA\Python\Scripts"
    if (Test-Path $poetryPath) {
        $env:PATH = "$poetryPath;$env:PATH"
    }
    
    Write-Host "✅ Poetry instalado" -ForegroundColor Green
} else {
    Write-Host "✅ Poetry ya está instalado" -ForegroundColor Green
}

# Instalar dependencias del backend
Write-Host "`n[3/4] Instalando dependencias del backend..." -ForegroundColor Yellow
Set-Location $rootPath
if (-not (Test-Path ".venv")) {
    poetry install --no-interaction
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencias ya instaladas" -ForegroundColor Green
}

# Verificar MongoDB
Write-Host "`n[4/4] Verificando MongoDB..." -ForegroundColor Yellow
$mongoTest = Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($mongoTest) {
    Write-Host "✅ MongoDB corriendo en puerto 27017" -ForegroundColor Green
} else {
    Write-Host "⚠️  MongoDB no responde. Iniciando con Docker..." -ForegroundColor Yellow
    docker-compose up -d mongodb
    Start-Sleep -Seconds 5
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "📦 INICIANDO SERVICIOS..." -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Iniciar User App (Puerto 3000)
Write-Host "🌐 Iniciando User App (puerto 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootPath\frontend\user-app'; Write-Host '🌐 USER APP - Puerto 3000' -ForegroundColor Cyan; npm run dev"

Start-Sleep -Seconds 2

# Iniciar Admin Dashboard (Puerto 3001)
Write-Host "🎛️  Iniciando Admin Dashboard (puerto 3001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootPath\frontend\admin-dashboard'; Write-Host '🎛️ ADMIN DASHBOARD - Puerto 3001' -ForegroundColor Cyan; npm run dev"

Start-Sleep -Seconds 2

# Iniciar Backend API (Puerto 8000)
Write-Host "⚙️  Iniciando Backend API (puerto 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootPath'; Write-Host '⚙️ BACKEND API - Puerto 8000' -ForegroundColor Cyan; poetry run uvicorn services.api-gateway.src.main:app --reload --host 0.0.0.0 --port 8000"

# Esperar que todos los servicios inicien
Write-Host "`n⏳ Esperando que los servicios inicien..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar servicios
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✅ SERVICIOS INICIADOS" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

$services = @(
    @{Name="User App"; Port=3000; URL="http://localhost:3000"},
    @{Name="Admin Dashboard"; Port=3001; URL="http://localhost:3001"},
    @{Name="Backend API"; Port=8000; URL="http://localhost:8000/docs"}
)

foreach ($svc in $services) {
    $test = Test-NetConnection -ComputerName localhost -Port $svc.Port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($test) {
        Write-Host "✅ $($svc.Name)" -ForegroundColor Green -NoNewline
        Write-Host " → $($svc.URL)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ $($svc.Name)" -ForegroundColor Red -NoNewline
        Write-Host " - No responde en puerto $($svc.Port)" -ForegroundColor Yellow
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "🎉 Proyecto iniciado exitosamente!" -ForegroundColor Green
Write-Host "`nPara detener todos los servicios:" -ForegroundColor White
Write-Host "   Cierra las ventanas de PowerShell abiertas" -ForegroundColor Gray
Write-Host "============================================`n" -ForegroundColor Cyan
