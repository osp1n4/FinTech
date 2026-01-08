# Script para generar datos de prueba en el sistema de detección de fraude

Write-Host "Generando datos de prueba para Fraud Detection System..." -ForegroundColor Cyan
Write-Host ""

# Usuarios de prueba
$users = @("user-001", "user-002", "user-003", "Paula05", "John99", "Maria123")

# Función para generar una transacción aleatoria
function New-TestTransaction {
    param(
        [string]$UserId,
        [decimal]$Amount,
        [bool]$IsSuspicious = $false
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    $transactionId = "txn-" + (Get-Random -Minimum 10000 -Maximum 99999)
    
    # Locaciones diferentes
    $locations = @(
        @{latitude = 40.7128; longitude = -74.0060},  # New York
        @{latitude = 34.0522; longitude = -118.2437}, # Los Angeles
        @{latitude = 41.8781; longitude = -87.6298},  # Chicago
        @{latitude = 29.7604; longitude = -95.3698},  # Houston
        @{latitude = 25.7617; longitude = -80.1918}   # Miami
    )
    
    $location = $locations | Get-Random
    
    $body = @{
        id = $transactionId
        user_id = $UserId
        amount = $Amount
        timestamp = $timestamp
        location = $location
    } | ConvertTo-Json -Compress
    
    return $body
}

Write-Host "Creando transacciones normales..." -ForegroundColor Yellow

# Generar 30 transacciones normales
$successCount = 0
$errorCount = 0

for ($i = 1; $i -le 30; $i++) {
    $user = $users | Get-Random
    $amount = Get-Random -Minimum 10 -Maximum 1400
    
    $body = New-TestTransaction -UserId $user -Amount $amount
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/evaluate" `
            -Method POST `
            -Body $body `
            -ContentType "application/json" `
            -UseBasicParsing `
            -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            $successCount++
            Write-Host "  ✓ Transacción $i creada (monto: $amount)" -ForegroundColor Green
        }
    } catch {
        $errorCount++
        Write-Host "  ✗ Error en transacción $i" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 200
}

Write-Host ""
Write-Host "Creando transacciones sospechosas (alto monto)..." -ForegroundColor Yellow

# Generar 10 transacciones sospechosas por monto alto
for ($i = 1; $i -le 10; $i++) {
    $user = $users | Get-Random
    $amount = Get-Random -Minimum 1600 -Maximum 5000
    
    $body = New-TestTransaction -UserId $user -Amount $amount -IsSuspicious $true
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/evaluate" `
            -Method POST `
            -Body $body `
            -ContentType "application/json" `
            -UseBasicParsing `
            -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            $successCount++
            Write-Host "  ✓ Transacción sospechosa $i creada (monto: $amount)" -ForegroundColor Yellow
        }
    } catch {
        $errorCount++
        Write-Host "  ✗ Error en transacción $i" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 200
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Resumen de generación de datos:" -ForegroundColor Cyan
Write-Host "  Exitosas: $successCount" -ForegroundColor Green
Write-Host "  Errores: $errorCount" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verificando datos en MongoDB..." -ForegroundColor Yellow

$count = docker exec fraud-mongodb mongosh -u admin -p fraud2026 --authenticationDatabase admin fraud_detection --quiet --eval "db.fraud_evaluations.countDocuments()"

Write-Host "Total de evaluaciones en BD: $count" -ForegroundColor Green
Write-Host ""
Write-Host "¡Datos de prueba generados exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Ahora puedes acceder a:" -ForegroundColor Yellow
Write-Host "  • Frontend Usuario: http://localhost:3000" -ForegroundColor White
Write-Host "  • Frontend Admin: http://localhost:3001" -ForegroundColor White
