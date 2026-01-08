# Screenshots

Esta carpeta almacena automáticamente las capturas de pantalla tomadas durante la ejecución de los tests.

## Convención de nombres

Los screenshots se guardan con el siguiente formato:
```
[nombre-descriptivo]-[timestamp].png
```

Ejemplos:
- `rules-modal-opened-2026-01-08T15-30-45.png`
- `transaction-approved-2026-01-08T15-31-12.png`
- `test-001-rule-created-2026-01-08T15-32-00.png`

## Screenshots automáticos

Playwright captura screenshots automáticamente en los siguientes casos:

1. **En fallos de tests**: Siempre que un test falla
2. **Capturas manuales**: Llamadas explícitas a `takeScreenshot()` en los tests
3. **En pasos importantes**: Configurado en cada Page Object

## Limpieza

Los screenshots se acumulan en esta carpeta. Se recomienda limpiarla periódicamente:

```powershell
# Eliminar todos los screenshots
Remove-Item screenshots\*.png
```

## Visualización

Los screenshots también están disponibles en:
- HTML Reporter: `npx playwright show-report`
- Trace Viewer: `npx playwright show-trace [trace-file]`
