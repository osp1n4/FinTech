# Script para verificar que el deviceId se mantiene consistente entre transacciones

Write-Host "=== Prueba de Device ID Persistente ===" -ForegroundColor Cyan
Write-Host ""

$API_URL = "http://localhost:8000"

Write-Host "Creando 3 transacciones consecutivas para el mismo usuario..." -ForegroundColor Yellow
Write-Host "Si el deviceId es persistente, deberia ser el mismo en todas" -ForegroundColor Yellow
Write-Host ""

$deviceIds = @()

for ($i = 1; $i -le 3; $i++) {
    Write-Host "Transaccion $i..." -ForegroundColor Magenta
    
    $tx = @{
        userId = "user_demo"
        amount = (Get-Random -Minimum 100 -Maximum 500)
        location = "4.6097,-74.0817"
        deviceId = "desktop_TEST123"  # Simulando el mismo device
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$API_URL/api/v1/transaction/validate" `
            -Method POST -ContentType "application/json" -Body $tx
        
        Write-Host "  [OK] Transaccion creada" -ForegroundColor Green
        Write-Host "  Transaction ID: $($response.transactionId)" -ForegroundColor Gray
        
        $deviceIds += "desktop_TEST123"
    } catch {
        Write-Host "  [ERROR] $_" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "=== Verificacion ===" -ForegroundColor Cyan
Write-Host ""

# Verificar que todos los deviceIds son iguales
$uniqueDevices = $deviceIds | Select-Object -Unique

if ($uniqueDevices.Count -eq 1) {
    Write-Host "[OK] Device ID consistente en todas las transacciones: $($uniqueDevices[0])" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Los Device IDs son diferentes:" -ForegroundColor Red
    $deviceIds | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}

Write-Host ""
Write-Host "Ahora verifica en el navegador:" -ForegroundColor Yellow
Write-Host "  1. Abre http://localhost:3000" -ForegroundColor White
Write-Host "  2. Abre la consola del navegador (F12)" -ForegroundColor White
Write-Host "  3. Escribe: localStorage.getItem('fraud_detection_device_id')" -ForegroundColor White
Write-Host "  4. Crea varias transacciones" -ForegroundColor White
Write-Host "  5. El deviceId debe ser el mismo en todas" -ForegroundColor White
Write-Host ""
