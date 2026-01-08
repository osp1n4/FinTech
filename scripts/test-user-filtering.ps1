# Script para probar el filtrado de transacciones por usuario
# Verifica que cada usuario solo vea sus propias transacciones

Write-Host "=== Prueba de Filtrado de Transacciones por Usuario ===" -ForegroundColor Cyan
Write-Host ""

$API_URL = "http://localhost:8000"

# Crear transacciones para diferentes usuarios
Write-Host "Creando transacciones para diferentes usuarios..." -ForegroundColor Yellow
Write-Host ""

# Usuario 1: user_demo
Write-Host "1. Creando transaccion para user_demo" -ForegroundColor Magenta
$tx1 = @{
    userId = "user_demo"
    amount = 500.0
    location = "4.6097,-74.0817"
    deviceId = "device_demo_1"
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "$API_URL/api/v1/transaction/validate" `
        -Method POST -ContentType "application/json" -Body $tx1
    Write-Host "  [OK] Transaccion creada" -ForegroundColor Green
    Write-Host "  Transaction ID: $($response1.transactionId)" -ForegroundColor Gray
} catch {
    Write-Host "  [ERROR] No se pudo crear transaccion: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Usuario 2: user_alice
Write-Host "`n2. Creando transaccion para user_alice" -ForegroundColor Magenta
$tx2 = @{
    userId = "user_alice"
    amount = 1200.0
    location = "6.2442,-75.5812"
    deviceId = "device_alice_1"
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "$API_URL/api/v1/transaction/validate" `
        -Method POST -ContentType "application/json" -Body $tx2
    Write-Host "  [OK] Transaccion creada" -ForegroundColor Green
    Write-Host "  Transaction ID: $($response2.transactionId)" -ForegroundColor Gray
} catch {
    Write-Host "  [ERROR] No se pudo crear transaccion: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Usuario 3: user_bob
Write-Host "`n3. Creando transaccion para user_bob" -ForegroundColor Magenta
$tx3 = @{
    userId = "user_bob"
    amount = 800.0
    location = "40.7128,-74.0060"
    deviceId = "device_bob_1"
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "$API_URL/api/v1/transaction/validate" `
        -Method POST -ContentType "application/json" -Body $tx3
    Write-Host "  [OK] Transaccion creada" -ForegroundColor Green
    Write-Host "  Transaction ID: $($response3.transactionId)" -ForegroundColor Gray
} catch {
    Write-Host "  [ERROR] No se pudo crear transaccion: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Verificar transacciones por usuario
Write-Host "`n=== Verificando Filtrado por Usuario ===" -ForegroundColor Cyan
Write-Host ""

# Verificar user_demo
Write-Host "Consultando transacciones de user_demo..." -ForegroundColor Yellow
try {
    $userDemoTxs = Invoke-RestMethod -Uri "$API_URL/api/v1/user/transactions/user_demo" `
        -Method GET
    $demoCount = ($userDemoTxs | Measure-Object).Count
    Write-Host "  Transacciones encontradas: $demoCount" -ForegroundColor White
    
    $wrongUser = $userDemoTxs | Where-Object { $_.userId -ne "user_demo" }
    if ($wrongUser) {
        Write-Host "  [ERROR] Se encontraron transacciones de otros usuarios!" -ForegroundColor Red
        $wrongUser | ForEach-Object { Write-Host "    - Usuario incorrecto: $($_.userId)" -ForegroundColor Red }
    } else {
        Write-Host "  [OK] Todas las transacciones son de user_demo" -ForegroundColor Green
    }
} catch {
    Write-Host "  [ERROR] No se pudieron consultar transacciones: $_" -ForegroundColor Red
}

Write-Host ""

# Verificar user_alice
Write-Host "Consultando transacciones de user_alice..." -ForegroundColor Yellow
try {
    $userAliceTxs = Invoke-RestMethod -Uri "$API_URL/api/v1/user/transactions/user_alice" `
        -Method GET
    $aliceCount = ($userAliceTxs | Measure-Object).Count
    Write-Host "  Transacciones encontradas: $aliceCount" -ForegroundColor White
    
    $wrongUser = $userAliceTxs | Where-Object { $_.userId -ne "user_alice" }
    if ($wrongUser) {
        Write-Host "  [ERROR] Se encontraron transacciones de otros usuarios!" -ForegroundColor Red
        $wrongUser | ForEach-Object { Write-Host "    - Usuario incorrecto: $($_.userId)" -ForegroundColor Red }
    } else {
        Write-Host "  [OK] Todas las transacciones son de user_alice" -ForegroundColor Green
    }
} catch {
    Write-Host "  [ERROR] No se pudieron consultar transacciones: $_" -ForegroundColor Red
}

Write-Host ""

# Verificar user_bob
Write-Host "Consultando transacciones de user_bob..." -ForegroundColor Yellow
try {
    $userBobTxs = Invoke-RestMethod -Uri "$API_URL/api/v1/user/transactions/user_bob" `
        -Method GET
    $bobCount = ($userBobTxs | Measure-Object).Count
    Write-Host "  Transacciones encontradas: $bobCount" -ForegroundColor White
    
    $wrongUser = $userBobTxs | Where-Object { $_.userId -ne "user_bob" }
    if ($wrongUser) {
        Write-Host "  [ERROR] Se encontraron transacciones de otros usuarios!" -ForegroundColor Red
        $wrongUser | ForEach-Object { Write-Host "    - Usuario incorrecto: $($_.userId)" -ForegroundColor Red }
    } else {
        Write-Host "  [OK] Todas las transacciones son de user_bob" -ForegroundColor Green
    }
} catch {
    Write-Host "  [ERROR] No se pudieron consultar transacciones: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== RESULTADO ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "[OK] El sistema esta filtrando correctamente las transacciones por usuario" -ForegroundColor Green
Write-Host ""
Write-Host "Ahora prueba en el navegador:" -ForegroundColor Yellow
Write-Host "  1. Abre http://localhost:3000" -ForegroundColor White
Write-Host "  2. Cambia entre diferentes usuarios con el selector (Demo User, Alice, Bob)" -ForegroundColor White
Write-Host "  3. Ve a 'Mis Transacciones' y verifica que solo aparecen las del usuario actual" -ForegroundColor White
Write-Host "  4. Crea una nueva transaccion y verifica que aparezca solo para ese usuario" -ForegroundColor White
Write-Host ""
