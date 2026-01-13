# Test de Aplicacion Dinamica de Reglas
# Verifica que los cambios en las reglas se aplican inmediatamente en las transacciones

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test: Aplicacion Dinamica de Reglas" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$analystId = "analyst_test"
$userId = "user_dynamic_test_$(Get-Random)"

# Limpiar datos previos
Write-Host "Limpiando datos previos de Redis..." -ForegroundColor Yellow
docker exec fraud-redis redis-cli DEL "rapid_tx:$userId" | Out-Null
docker exec fraud-redis redis-cli DEL "user_devices:$userId" | Out-Null
Write-Host ""

# Funcion para hacer transaccion
function Test-Transaction {
    param([string]$description, [decimal]$amount)
    
    Write-Host ">>> $description" -ForegroundColor Magenta
    
    $testData = @{
        amount = $amount
        userId = $userId
        location = "Bogota"
        deviceId = "device_dynamic_test"
    } | ConvertTo-Json -Depth 3
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transaction/validate" -Method Post -Body $testData -ContentType "application/json" -TimeoutSec 10
        
        Write-Host "  Status: $($response.status)" -ForegroundColor White
        Write-Host "  Risk Score: $($response.riskScore)" -ForegroundColor White
        Write-Host "  Violaciones:" -ForegroundColor White
        
        if ($response.violations.Count -eq 0) {
            Write-Host "    Ninguna" -ForegroundColor Green
        } else {
            foreach ($v in $response.violations) {
                Write-Host "    - $v" -ForegroundColor Yellow
            }
        }
        Write-Host ""
        
        return $response
    } catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
        Write-Host ""
        return $null
    }
}

# Funcion para editar regla
function Edit-Rule {
    param([string]$ruleId, [hashtable]$parameters, [string]$description)
    
    Write-Host ">>> $description" -ForegroundColor Cyan
    
    $body = @{ parameters = $parameters } | ConvertTo-Json
    $headers = @{
        "Content-Type" = "application/json"
        "X-Analyst-ID" = $analystId
    }
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/rules/$ruleId" -Method Put -Body $body -Headers $headers
        Write-Host "  Regla actualizada exitosamente" -ForegroundColor Green
        Write-Host ""
    } catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
        Write-Host ""
    }
}

# PRUEBA 1: Cambiar limite de transacciones rapidas
Write-Host "===== PRUEBA 1: Transacciones Rapidas =====" -ForegroundColor Cyan
Write-Host ""

Write-Host "Configuracion inicial: max_transactions=5, window=10 minutos (del test anterior)" -ForegroundColor Yellow
Write-Host ""

# Hacer 3 transacciones (deberia estar OK con limite de 5)
$r1 = Test-Transaction "Transaccion 1 de 3 (limite: 5)" 100
Start-Sleep -Seconds 1
$r2 = Test-Transaction "Transaccion 2 de 3 (limite: 5)" 150
Start-Sleep -Seconds 1
$r3 = Test-Transaction "Transaccion 3 de 3 (limite: 5)" 200

# Cambiar limite a 2 transacciones
Edit-Rule "rule_rapid_transaction" @{max_transactions=2; time_window_minutes=10} "Cambiar limite a 2 transacciones en 10 minutos"

# Hacer una transaccion mas (ahora deberia violar porque tenemos 4 transacciones y el limite es 2)
Write-Host "Esperando 3 segundos para que se aplique el cambio..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
$r4 = Test-Transaction "Transaccion 4 (nuevo limite: 2, deberia violar)" 250

$hasViolation = $r4.violations -contains "rapid_transactions_detected"
if ($hasViolation) {
    Write-Host "OK - La violacion se detecto correctamente con el nuevo limite" -ForegroundColor Green
} else {
    Write-Host "ERROR - No se detecto la violacion con el nuevo limite" -ForegroundColor Red
}
Write-Host ""

# PRUEBA 2: Cambiar threshold de monto
Write-Host "===== PRUEBA 2: Monto Alto =====" -ForegroundColor Cyan
Write-Host ""

# Limpiar transacciones anteriores
docker exec fraud-redis redis-cli DEL "rapid_tx:$userId" | Out-Null

Write-Host "Configuracion inicial: threshold=1500" -ForegroundColor Yellow
Write-Host ""

# Transaccion bajo el limite
$t1 = Test-Transaction "Transaccion de $1000 (limite: 1500)" 1000

# Cambiar threshold a 800
Edit-Rule "rule_amount_threshold" @{threshold=800} "Cambiar threshold a $800"

# Transaccion que ahora supera el limite
Start-Sleep -Seconds 2
$t2 = Test-Transaction "Transaccion de $1000 (nuevo limite: 800, deberia violar)" 1000

$hasAmountViolation = $t2.violations -contains "amount_threshold_exceeded"
if ($hasAmountViolation) {
    Write-Host "OK - La violacion de monto se detecto con el nuevo threshold" -ForegroundColor Green
} else {
    Write-Host "ERROR - No se detecto la violacion de monto con el nuevo threshold" -ForegroundColor Red
}
Write-Host ""

# PRUEBA 3: Desactivar regla
Write-Host "===== PRUEBA 3: Desactivar Regla =====" -ForegroundColor Cyan
Write-Host ""

# Desactivar la regla de monto alto
Edit-Rule "rule_amount_threshold" @{enabled=$false} "Desactivar regla de monto alto"

# Transaccion alta que ahora NO deberia violar
Start-Sleep -Seconds 2
$t3 = Test-Transaction "Transaccion de $5000 (regla desactivada)" 5000

$hasAmountViolation2 = $t3.violations -contains "amount_threshold_exceeded"
if (-not $hasAmountViolation2) {
    Write-Host "OK - La regla desactivada no genero violacion" -ForegroundColor Green
} else {
    Write-Host "ERROR - La regla desactivada aun genera violacion" -ForegroundColor Red
}
Write-Host ""

# Restaurar configuracion
Write-Host "===== Restaurando Configuracion =====" -ForegroundColor Yellow
Edit-Rule "rule_amount_threshold" @{threshold=1500; enabled=$true} "Restaurar threshold a 1500 y reactivar"
Edit-Rule "rule_rapid_transaction" @{max_transactions=3; time_window_minutes=5} "Restaurar limite a 3 transacciones en 5 minutos"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test completado" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
