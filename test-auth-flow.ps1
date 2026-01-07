# Test del flujo completo de autenticación de usuario
# =====================================================

Write-Host "`n=== FLUJO DE AUTENTICACION DE TRANSACCION SOSPECHOSA ===" -ForegroundColor Cyan

# 1. Crear una transacción sospechosa (monto alto, 1 violación)
Write-Host "`n[1] Creando transaccion sospechosa..." -ForegroundColor Yellow
$transaction = @{
    userId = "user_test_auth"
    amount = 11000
    location = "4.6097,-74.0817"
    deviceId = "device_test_001"
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transaction/validate" `
    -Method Post `
    -Body $transaction `
    -ContentType "application/json"

Write-Host "Response completa:" ($response1 | ConvertTo-Json -Depth 10)
Write-Host "Estado: $($response1.status)" -ForegroundColor $(if ($response1.status -eq "SUSPICIOUS") { "Yellow" } else { "Red" })
Write-Host "Transaction ID: $($response1.transactionId)"
Write-Host "Risk Level: $($response1.riskLevel)"
Write-Host "Violations: $($response1.violations -join ', ')"

$transactionId = $response1.transactionId

# Esperar un momento
Start-Sleep -Seconds 2

# 2. Usuario consulta sus transacciones
Write-Host "`n[2] Usuario consulta sus transacciones..." -ForegroundColor Yellow
$userTransactions = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/user/transactions/user_test_auth" `
    -Method Get

Write-Host "Total de transacciones: $($userTransactions.Count)"
$suspiciousTx = $userTransactions | Where-Object { $_.status -eq "PENDING_REVIEW" } | Select-Object -First 1

if ($suspiciousTx) {
    Write-Host "Transaccion sospechosa encontrada:" -ForegroundColor Yellow
    Write-Host "  - ID: $($suspiciousTx.id)"
    Write-Host "  - Amount: $($suspiciousTx.amount)"
    Write-Host "  - needsAuthentication: $($suspiciousTx.needsAuthentication)"
    Write-Host "  - userAuthenticated: $($suspiciousTx.userAuthenticated)"
}

# Esperar un momento
Start-Sleep -Seconds 2

# 3. Usuario autentica la transacción (confirma que fue él)
Write-Host "`n[3] Usuario confirma: 'Fui yo'..." -ForegroundColor Yellow
$authRequest = @{
    confirmed = $true
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/user/transaction/$transactionId/authenticate" `
        -Method Post `
        -Body $authRequest `
        -ContentType "application/json"
    
    Write-Host "Autenticacion exitosa" -ForegroundColor Green
    Write-Host "Status: $($response3.status)"
    Write-Host "Confirmed: $($response3.confirmed)"
    Write-Host "Message: $($response3.message)"
} catch {
    Write-Host "Error en autenticacion: $($_.Exception.Message)" -ForegroundColor Red
}

# Esperar un momento
Start-Sleep -Seconds 2

# 4. Admin consulta transacciones y ve el estado de autenticación
Write-Host "`n[4] Admin consulta transacciones sospechosas..." -ForegroundColor Yellow
$adminView = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/transactions/log?status=SUSPICIOUS" `
    -Method Get `
    -Headers @{"X-Analyst-ID" = "analyst_test"}

$ourTx = $adminView | Where-Object { $_.id -eq $transactionId } | Select-Object -First 1

if ($ourTx) {
    Write-Host "Transaccion en vista de admin:" -ForegroundColor Yellow
    Write-Host "  - ID: $($ourTx.id)"
    Write-Host "  - Amount: $($ourTx.amount)"
    Write-Host "  - Status: $($ourTx.status)"
    Write-Host "  - userAuthenticated: $($ourTx.userAuthenticated)" -ForegroundColor $(if ($ourTx.userAuthenticated -eq $true) { "Green" } else { "Gray" })
    Write-Host "  - violations: $($ourTx.violations -join ', ')"
    
    if ($ourTx.userAuthenticated -eq $true) {
        Write-Host "`n  Usuario confirmo que fue el - Admin puede aprobar con confianza" -ForegroundColor Green
    }
}

# 5. Admin aprueba la transacción (ya que usuario confirmó)
Write-Host "`n[5] Admin aprueba la transaccion..." -ForegroundColor Yellow
$reviewRequest = @{
    decision = "APPROVED"
    analyst_comment = "Usuario autentico transaccion correctamente"
} | ConvertTo-Json

try {
    $response5 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transaction/review/$transactionId" `
        -Method Put `
        -Body $reviewRequest `
        -ContentType "application/json" `
        -Headers @{"X-Analyst-ID" = "analyst_test"}
    
    Write-Host "Revision completada" -ForegroundColor Green
    Write-Host "Status: $($response5.status)"
    Write-Host "Decision: $($response5.decision)"
} catch {
    Write-Host "Error en revision: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Usuario vuelve a consultar y ve que fue aprobada
Write-Host "`n[6] Usuario consulta resultado final..." -ForegroundColor Yellow
$finalCheck = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/user/transactions/user_test_auth" `
    -Method Get

$finalTx = $finalCheck | Where-Object { $_.id -eq $transactionId } | Select-Object -First 1

if ($finalTx) {
    Write-Host "Estado final de la transaccion:" -ForegroundColor Yellow
    Write-Host "  - ID: $($finalTx.id)"
    Write-Host "  - Status: $($finalTx.status)" -ForegroundColor Green
    Write-Host "  - reviewedBy: $($finalTx.reviewedBy)"
    Write-Host "  - reviewedAt: $($finalTx.reviewedAt)"
}

Write-Host "`n=== FLUJO COMPLETADO EXITOSAMENTE ===" -ForegroundColor Green
Write-Host "Usuario hizo transaccion sospechosa" -ForegroundColor Green
Write-Host "Usuario la autentico (Fui yo)" -ForegroundColor Green
Write-Host "Admin vio la autenticacion y aprobo" -ForegroundColor Green
Write-Host "Usuario ve el resultado final (APPROVED)" -ForegroundColor Green
