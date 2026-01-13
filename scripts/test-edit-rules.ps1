# Test de Edicion de Reglas
# Verifica que se pueden editar los parametros de las reglas device_validation y rapid_transaction

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test: Edicion de Reglas" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$analystId = "analyst_test"

# 1. Obtener reglas actuales
Write-Host "1. Obteniendo reglas actuales..." -ForegroundColor Yellow
try {
    $rules = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/rules" -Method Get
    
    $deviceRule = $rules | Where-Object { $_.id -eq "rule_device_validation" }
    $rapidRule = $rules | Where-Object { $_.id -eq "rule_rapid_transaction" }
    
    Write-Host "  RuleValidacionDispositivo:" -ForegroundColor White
    Write-Host "    device_memory_days: $($deviceRule.parameters.device_memory_days)" -ForegroundColor Gray
    
    Write-Host "  RuleTransaccionesRapidas:" -ForegroundColor White
    Write-Host "    max_transactions: $($rapidRule.parameters.max_transactions)" -ForegroundColor Gray
    Write-Host "    time_window_minutes: $($rapidRule.parameters.time_window_minutes)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
    exit 1
}

# 2. Editar RuleValidacionDispositivo
Write-Host "2. Editando RuleValidacionDispositivo (device_memory_days: 90 -> 60)..." -ForegroundColor Yellow
$deviceUpdate = @{
    parameters = @{
        device_memory_days = 60
    }
} | ConvertTo-Json

try {
    $headers = @{
        "Content-Type" = "application/json"
        "X-Analyst-ID" = $analystId
    }
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/rules/rule_device_validation" -Method Put -Body $deviceUpdate -Headers $headers
    Write-Host "  Actualizado exitosamente" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
    Write-Host ""
}

# 3. Editar RuleTransaccionesRapidas
Write-Host "3. Editando RuleTransaccionesRapidas (max: 3->5, window: 5->10)..." -ForegroundColor Yellow
$rapidUpdate = @{
    parameters = @{
        max_transactions = 5
        time_window_minutes = 10
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/rules/rule_rapid_transaction" -Method Put -Body $rapidUpdate -Headers $headers
    Write-Host "  Actualizado exitosamente" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
    Write-Host ""
}

# 4. Verificar cambios
Write-Host "4. Verificando cambios..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $rules = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/rules" -Method Get
    
    $deviceRule = $rules | Where-Object { $_.id -eq "rule_device_validation" }
    $rapidRule = $rules | Where-Object { $_.id -eq "rule_rapid_transaction" }
    
    Write-Host "  RuleValidacionDispositivo:" -ForegroundColor White
    $deviceMemory = $deviceRule.parameters.device_memory_days
    Write-Host "    device_memory_days: $deviceMemory" -ForegroundColor $(if ($deviceMemory -eq 60) { "Green" } else { "Red" })
    
    Write-Host "  RuleTransaccionesRapidas:" -ForegroundColor White
    $maxTx = $rapidRule.parameters.max_transactions
    $timeWindow = $rapidRule.parameters.time_window_minutes
    Write-Host "    max_transactions: $maxTx" -ForegroundColor $(if ($maxTx -eq 5) { "Green" } else { "Red" })
    Write-Host "    time_window_minutes: $timeWindow" -ForegroundColor $(if ($timeWindow -eq 10) { "Green" } else { "Red" })
    Write-Host ""
    
    # Validar resultados
    $deviceOk = $deviceMemory -eq 60
    $rapidOk = ($maxTx -eq 5) -and ($timeWindow -eq 10)
    
    if ($deviceOk -and $rapidOk) {
        Write-Host "TEST PASADO - Todas las reglas se editaron correctamente" -ForegroundColor Green
    } else {
        Write-Host "TEST FALLIDO - Algunas reglas no se actualizaron" -ForegroundColor Red
    }
    
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verificando Redis..." -ForegroundColor Yellow
docker exec fraud-redis redis-cli KEYS "rule_config:*"
Write-Host "========================================" -ForegroundColor Cyan
