#!/usr/bin/env pwsh
# Script para ejecutar todos los tests E2E corregidos

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EJECUTANDO TESTS E2E" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testFiles = @(
    "tests/hu-001-reception.spec.ts",
    "tests/hu-002-audit.spec.ts",
    "tests/hu-003-007-fraud-strategies.spec.ts",
    "tests/hu-008-009-config.spec.ts",
    "tests/hu-012-manual-review.spec.ts",
    "tests/hu-013-user-dashboard.spec.ts",
    "tests/hu-014-admin-metrics.spec.ts"
)

$totalPassed = 0
$totalFailed = 0
$totalFlaky = 0

foreach ($testFile in $testFiles) {
    $testName = $testFile -replace "tests/", "" -replace ".spec.ts", ""
    Write-Host "`n--- Ejecutando: $testName ---" -ForegroundColor Yellow
    
    $output = npx playwright test $testFile --project=chromium --reporter=list 2>&1 | Out-String
    Write-Host $output
    
    # Extraer resultados
    if ($output -match "(\d+) passed") {
        $passed = [int]$Matches[1]
        $totalPassed += $passed
    }
    if ($output -match "(\d+) failed") {
        $failed = [int]$Matches[1]
        $totalFailed += $failed
    }
    if ($output -match "(\d+) flaky") {
        $flaky = [int]$Matches[1]
        $totalFlaky += $flaky
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RESUMEN FINAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total Passed: $totalPassed" -ForegroundColor Green
Write-Host "Total Failed: $totalFailed" -ForegroundColor Red
Write-Host "Total Flaky: $totalFlaky" -ForegroundColor Yellow
Write-Host ""
