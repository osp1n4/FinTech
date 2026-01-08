# ========================================
# Script de Validación de Reglas de Ubicación
# Fraud Detection Engine
# ========================================

param(
    [string]$UserId = "user_location_test_$(Get-Date -Format 'HHmmss')",
    [string]$ApiUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"

# Colores
$cyan = "Cyan"
$green = "Green"
$yellow = "Yellow"
$red = "Red"

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor $cyan
Write-Host "║  VALIDACIÓN DE REGLAS DE UBICACIÓN                      ║" -ForegroundColor $cyan
Write-Host "║  Fraud Detection Engine                                 ║" -ForegroundColor $cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor $cyan

Write-Host "`nUser ID: $UserId" -ForegroundColor $yellow
Write-Host "API URL: $ApiUrl`n" -ForegroundColor $yellow

# ========================================
# PRUEBA 1: Primera transacción (Nueva York)
# ========================================
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor $cyan
Write-Host "│ PRUEBA 1: Primera transacción desde Nueva York         │" -ForegroundColor $cyan
Write-Host "│ Lat: 40.7128, Lon: -74.0060                            │" -ForegroundColor $cyan
Write-Host "│ Esperado: LOW_RISK (no_historical_location)            │" -ForegroundColor $cyan
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor $cyan

$body1 = @{
    id = "txn_loc_01_$(Get-Date -Format 'HHmmss')"
    amount = 500
    user_id = $UserId
    location = @{
        latitude = 40.7128
        longitude = -74.0060
    }
} | ConvertTo-Json

try {
    $result1 = Invoke-RestMethod -Uri "$ApiUrl/transaction" -Method POST -ContentType "application/json" -Body $body1
    Write-Host "✓ Resultado: $($result1.risk_level)" -ForegroundColor $(if ($result1.risk_level -eq "LOW_RISK") { $green } else { $red })
    Write-Host "  Transaction ID: $($result1.transaction_id)" -ForegroundColor $yellow
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor $red
    exit 1
}

Start-Sleep -Seconds 2

# Verificar Redis
Write-Host "`n📦 Verificando Redis..." -ForegroundColor $yellow
try {
    $redisResult = docker exec fraud-redis redis-cli GET "user:$UserId:location"
    Write-Host "  Ubicación guardada: $redisResult" -ForegroundColor $green
} catch {
    Write-Host "  ⚠ No se pudo verificar Redis" -ForegroundColor $yellow
}

Start-Sleep -Seconds 2

# ========================================
# PRUEBA 2: Transacción cercana (Brooklyn - ~7.5 km)
# ========================================
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor $cyan
Write-Host "│ PRUEBA 2: Transacción desde Brooklyn                   │" -ForegroundColor $cyan
Write-Host "│ Lat: 40.6782, Lon: -73.9442                            │" -ForegroundColor $cyan
Write-Host "│ Distancia: ~7.5 km desde NY                            │" -ForegroundColor $cyan
Write-Host "│ Esperado: LOW_RISK (dentro del radio de 100 km)       │" -ForegroundColor $cyan
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor $cyan

$body2 = @{
    id = "txn_loc_02_$(Get-Date -Format 'HHmmss')"
    amount = 800
    user_id = $UserId
    location = @{
        latitude = 40.6782
        longitude = -73.9442
    }
} | ConvertTo-Json

try {
    $result2 = Invoke-RestMethod -Uri "$ApiUrl/transaction" -Method POST -ContentType "application/json" -Body $body2
    Write-Host "✓ Resultado: $($result2.risk_level)" -ForegroundColor $(if ($result2.risk_level -eq "LOW_RISK") { $green } else { $red })
    Write-Host "  Transaction ID: $($result2.transaction_id)" -ForegroundColor $yellow
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor $red
}

Start-Sleep -Seconds 2

# ========================================
# PRUEBA 3: Transacción lejana (Philadelphia - ~130 km)
# ========================================
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor $cyan
Write-Host "│ PRUEBA 3: Transacción desde Philadelphia               │" -ForegroundColor $cyan
Write-Host "│ Lat: 39.9526, Lon: -75.1652                            │" -ForegroundColor $cyan
Write-Host "│ Distancia: ~130 km desde Brooklyn                      │" -ForegroundColor $cyan
Write-Host "│ Esperado: HIGH_RISK (fuera del radio de 100 km)       │" -ForegroundColor $cyan
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor $cyan

$body3 = @{
    id = "txn_loc_03_$(Get-Date -Format 'HHmmss')"
    amount = 1200
    user_id = $UserId
    location = @{
        latitude = 39.9526
        longitude = -75.1652
    }
} | ConvertTo-Json

try {
    $result3 = Invoke-RestMethod -Uri "$ApiUrl/transaction" -Method POST -ContentType "application/json" -Body $body3
    Write-Host "✓ Resultado: $($result3.risk_level)" -ForegroundColor $(if ($result3.risk_level -eq "HIGH_RISK") { $green } else { $red })
    Write-Host "  Transaction ID: $($result3.transaction_id)" -ForegroundColor $yellow
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor $red
}

Start-Sleep -Seconds 2

# ========================================
# PRUEBA 4: Transacción muy lejana (Miami - ~1,760 km)
# ========================================
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor $cyan
Write-Host "│ PRUEBA 4: Transacción desde Miami                      │" -ForegroundColor $cyan
Write-Host "│ Lat: 25.7617, Lon: -80.1918                            │" -ForegroundColor $cyan
Write-Host "│ Distancia: ~1,760 km desde Philadelphia                │" -ForegroundColor $cyan
Write-Host "│ Esperado: HIGH_RISK (muy fuera del radio)             │" -ForegroundColor $cyan
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor $cyan

$body4 = @{
    id = "txn_loc_04_$(Get-Date -Format 'HHmmss')"
    amount = 500
    user_id = $UserId
    location = @{
        latitude = 25.7617
        longitude = -80.1918
    }
} | ConvertTo-Json

try {
    $result4 = Invoke-RestMethod -Uri "$ApiUrl/transaction" -Method POST -ContentType "application/json" -Body $body4
    Write-Host "✓ Resultado: $($result4.risk_level)" -ForegroundColor $(if ($result4.risk_level -eq "HIGH_RISK") { $green } else { $red })
    Write-Host "  Transaction ID: $($result4.transaction_id)" -ForegroundColor $yellow
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor $red
}

Start-Sleep -Seconds 2

# ========================================
# RESUMEN
# ========================================
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor $green
Write-Host "║  RESUMEN DE EVALUACIONES                                ║" -ForegroundColor $green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor $green

try {
    $evaluations = Invoke-RestMethod -Uri "$ApiUrl/audit/user/$UserId" -Method GET
    
    Write-Host "`nTotal de transacciones: $($evaluations.Count)" -ForegroundColor $yellow
    Write-Host ""
    
    foreach ($eval in $evaluations) {
        $color = switch ($eval.risk_level) {
            "LOW_RISK" { $green }
            "MEDIUM_RISK" { $yellow }
            "HIGH_RISK" { $red }
            default { "White" }
        }
        
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $color
        Write-Host "Transaction ID: $($eval.transaction_id)" -ForegroundColor White
        Write-Host "Risk Level    : $($eval.risk_level)" -ForegroundColor $color
        Write-Host "Reasons       : $($eval.reasons -join ', ')" -ForegroundColor White
        Write-Host "Status        : $($eval.status)" -ForegroundColor White
        Write-Host "Evaluated At  : $($eval.evaluated_at)" -ForegroundColor White
        Write-Host ""
    }
    
    # Estadísticas
    $lowRisk = ($evaluations | Where-Object { $_.risk_level -eq "LOW_RISK" }).Count
    $highRisk = ($evaluations | Where-Object { $_.risk_level -eq "HIGH_RISK" }).Count
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White
    Write-Host "Estadísticas:" -ForegroundColor $yellow
    Write-Host "  ✓ LOW_RISK : $lowRisk" -ForegroundColor $green
    Write-Host "  ⚠ HIGH_RISK: $highRisk" -ForegroundColor $red
    
} catch {
    Write-Host "✗ Error al obtener resumen: $($_.Exception.Message)" -ForegroundColor $red
}

# Verificar RabbitMQ
Write-Host "`n📨 Verificando cola de revisión manual en RabbitMQ..." -ForegroundColor $yellow
Write-Host "   URL: http://localhost:15672 (usuario: fraud, password: fraud2026)" -ForegroundColor $cyan

Write-Host "`n✓ Validación completada!" -ForegroundColor $green
Write-Host "`nPara más detalles, ver LOCATION_RULES_GUIDE.md`n" -ForegroundColor $cyan
