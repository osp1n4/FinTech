# Script de prueba para ubicación GPS
# Verifica que el sistema acepta coordenadas en formato "lat,lon"

Write-Host "=== Prueba de Ubicación GPS ===" -ForegroundColor Cyan
Write-Host ""

# URL de la API
$API_URL = "http://localhost:8000"

# Función para enviar transacción con coordenadas
function Test-TransactionWithCoordinates {
    param(
        [string]$Location,
        [string]$Description
    )
    
    Write-Host "Probando: $Description" -ForegroundColor Yellow
    Write-Host "Ubicación: $Location"
    
    $body = @{
        userId = "user_demo"
        amount = 1000.0
        location = $Location
        deviceId = "test-device-gps"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$API_URL/api/v1/transaction/validate" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body
        
        Write-Host "✅ Transacción creada exitosamente" -ForegroundColor Green
        Write-Host "   Transaction ID: $($response.transaction_id)"
        Write-Host "   Risk Score: $($response.risk_score)"
        Write-Host ""
        return $true
    } catch {
        Write-Host "❌ Error al crear transacción:" -ForegroundColor Red
        Write-Host "   $_"
        Write-Host ""
        return $false
    }
}

# Test 1: Coordenadas GPS (Bogotá)
Write-Host "`n--- Test 1: Coordenadas GPS de Bogotá ---" -ForegroundColor Magenta
$test1 = Test-TransactionWithCoordinates -Location "4.6097,-74.0817" -Description "GPS Bogotá"

Start-Sleep -Seconds 1

# Test 2: Coordenadas GPS (Medellín)
Write-Host "`n--- Test 2: Coordenadas GPS de Medellín ---" -ForegroundColor Magenta
$test2 = Test-TransactionWithCoordinates -Location "6.2442,-75.5812" -Description "GPS Medellín"

Start-Sleep -Seconds 1

# Test 3: Coordenadas GPS (New York)
Write-Host "`n--- Test 3: Coordenadas GPS de New York ---" -ForegroundColor Magenta
$test3 = Test-TransactionWithCoordinates -Location "40.7128,-74.0060" -Description "GPS New York"

Start-Sleep -Seconds 1

# Test 4: Nombre de ciudad (Fallback)
Write-Host "`n--- Test 4: Nombre de Ciudad (Fallback) ---" -ForegroundColor Magenta
$test4 = Test-TransactionWithCoordinates -Location "Miami, USA" -Description "Texto Miami"

Start-Sleep -Seconds 1

# Test 5: Coordenadas con decimales
Write-Host "`n--- Test 5: Coordenadas con más decimales ---" -ForegroundColor Magenta
$test5 = Test-TransactionWithCoordinates -Location "3.4516,-76.5320" -Description "GPS Cali (4 decimales)"

# Resumen
Write-Host "`n=== RESUMEN DE PRUEBAS ===" -ForegroundColor Cyan
Write-Host "Test 1 (GPS Bogotá):    $(if($test1){'✅'}else{'❌'})"
Write-Host "Test 2 (GPS Medellín):  $(if($test2){'✅'}else{'❌'})"
Write-Host "Test 3 (GPS New York):  $(if($test3){'✅'}else{'❌'})"
Write-Host "Test 4 (Texto Miami):   $(if($test4){'✅'}else{'❌'})"
Write-Host "Test 5 (GPS Cali):      $(if($test5){'✅'}else{'❌'})"

$passCount = @($test1, $test2, $test3, $test4, $test5) | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "`nPruebas exitosas: $passCount/5" -ForegroundColor $(if($passCount -eq 5){'Green'}else{'Yellow'})

if ($passCount -eq 5) {
    Write-Host "`n[OK] Todas las pruebas pasaron! El sistema GPS funciona correctamente." -ForegroundColor Green
    Write-Host "Ahora puedes probar en el navegador:" -ForegroundColor Cyan
    Write-Host "  1. Abre http://localhost:3000" -ForegroundColor White
    Write-Host "  2. Haz clic en Nueva Transaccion" -ForegroundColor White
    Write-Host "  3. Haz clic en el boton Usar Ubicacion GPS" -ForegroundColor White
    Write-Host "  4. Acepta el permiso del navegador" -ForegroundColor White
    Write-Host "  5. Verifica que el campo se llene con coordenadas" -ForegroundColor White
} else {
    Write-Host "`n[!] Algunas pruebas fallaron. Revisa los errores anteriores." -ForegroundColor Yellow
}
