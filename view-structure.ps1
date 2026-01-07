# Script para visualizar la estructura de microservicios del proyecto
# Ejecutar: .\view-structure.ps1

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🏗️  FRAUD DETECTION ENGINE - ARQUITECTURA DE MICROSERVICIOS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📂 Estructura del Proyecto:" -ForegroundColor Yellow
Write-Host ""

# Función para mostrar estructura con colores
function Show-Tree {
    param (
        [string]$Path,
        [string]$Prefix = "",
        [int]$Level = 0
    )
    
    if ($Level -gt 3) { return }
    
    $items = Get-ChildItem -Path $Path -ErrorAction SilentlyContinue | 
             Where-Object { $_.Name -notmatch '^(\.git|__pycache__|\.venv|node_modules|dist|build)$' }
    
    foreach ($item in $items) {
        $icon = if ($item.PSIsContainer) { "📁" } else { "📄" }
        $color = if ($item.PSIsContainer) { "White" } else { "Gray" }
        
        Write-Host "$Prefix$icon $($item.Name)" -ForegroundColor $color
        
        if ($item.PSIsContainer -and $Level -lt 2) {
            Show-Tree -Path $item.FullName -Prefix "$Prefix  " -Level ($Level + 1)
        }
    }
}

# Mostrar microservicios
Write-Host "🔷 MICROSERVICIOS:" -ForegroundColor Green
Write-Host ""

if (Test-Path "services") {
    $services = Get-ChildItem -Path "services" -Directory
    foreach ($service in $services) {
        Write-Host "  ├─ $($service.Name)" -ForegroundColor Cyan
        
        $readmePath = Join-Path $service.FullName "README.md"
        if (Test-Path $readmePath) {
            Write-Host "     ├─ ✅ README.md (Documentado)" -ForegroundColor Green
        }
        
        $dockerfilePath = Join-Path $service.FullName "Dockerfile"
        if (Test-Path $dockerfilePath) {
            Write-Host "     ├─ 🐳 Dockerfile" -ForegroundColor Blue
        }
        
        $srcPath = Join-Path $service.FullName "src"
        if (Test-Path $srcPath) {
            $fileCount = (Get-ChildItem -Path $srcPath -Recurse -File -Filter "*.py").Count
            Write-Host "     └─ 📝 $fileCount archivos Python" -ForegroundColor White
        }
        Write-Host ""
    }
}

Write-Host ""
Write-Host "🗄️ INFRAESTRUCTURA:" -ForegroundColor Yellow
Write-Host "  ├─ MongoDB (Puerto 27017)" -ForegroundColor White
Write-Host "  ├─ Redis (Puerto 6379)" -ForegroundColor White
Write-Host "  └─ RabbitMQ (Puertos 5672, 15672)" -ForegroundColor White
Write-Host ""

Write-Host "📊 ESTADO DE DOCKER:" -ForegroundColor Magenta
Write-Host ""

$containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null
if ($LASTEXITCODE -eq 0) {
    $containers | ForEach-Object {
        if ($_ -match "fraud-") {
            Write-Host "  ✅ $_" -ForegroundColor Green
        }
    }
} else {
    Write-Host "  ⚠️  Docker no está corriendo o no hay contenedores activos" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📚 DOCUMENTACIÓN DISPONIBLE:" -ForegroundColor Cyan
Write-Host ""

$docs = @(
    "README.md",
    "MICROSERVICES_ARCHITECTURE.md",
    "PROJECT_STRUCTURE.md",
    "QUICKSTART.md",
    "IMPLEMENTATION_SUMMARY.md"
)

foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Write-Host "  ✅ $doc" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $doc (No encontrado)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 COMANDOS RÁPIDOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Levantar microservicios:" -ForegroundColor White
Write-Host "    docker-compose -f docker-compose.microservices.yml up --build" -ForegroundColor Gray
Write-Host ""
Write-Host "  Ver logs:" -ForegroundColor White
Write-Host "    docker logs fraud-api-gateway -f" -ForegroundColor Gray
Write-Host ""
Write-Host "  Escalar servicios:" -ForegroundColor White
Write-Host "    docker-compose up --scale worker-service=3" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
