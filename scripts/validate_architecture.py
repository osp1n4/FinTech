"""
Script de validación de Clean Architecture
Verifica que Domain no importe de Infrastructure (FT-007)

Cumple: Regla del Crítico - Validación automatizada de arquitectura

Nota del desarrollador (María Gutiérrez):
La IA no propuso validación automática. Implementé este script para
garantizar que no se viole la Clean Architecture inadvertidamente.
Esto previene deuda técnica y mantiene la separación de capas.
"""
import ast
import sys
from pathlib import Path


def check_domain_imports():
    """
    Verifica que la capa Domain no importe de Infrastructure
    
    Returns:
        True si la arquitectura es válida, False si hay violaciones
    """
    print("🔍 Validando Clean Architecture...")
    print("=" * 60)

    domain_path = Path("src/domain")
    if not domain_path.exists():
        print("❌ Error: Carpeta src/domain no encontrada")
        return False

    violations = []

    # Revisar todos los archivos Python en domain/
    for python_file in domain_path.rglob("*.py"):
        if python_file.name == "__init__.py":
            continue

        with open(python_file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=str(python_file))
            except SyntaxError as e:
                print(f"⚠️  Warning: Syntax error in {python_file}: {e}")
                continue

        # Analizar imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "infrastructure" in alias.name:
                        violations.append(
                            f"{python_file.relative_to('.')}: imports {alias.name}"
                        )

            elif isinstance(node, ast.ImportFrom):
                if node.module and "infrastructure" in node.module:
                    violations.append(
                        f"{python_file.relative_to('.')}: imports from {node.module}"
                    )

    # Reportar resultados
    if violations:
        print("❌ VIOLACIONES DE CLEAN ARCHITECTURE DETECTADAS:")
        print()
        for violation in violations:
            print(f"  ❌ {violation}")
        print()
        print("La capa Domain NO debe importar de Infrastructure")
        print("Esto viola el principio de Dependency Inversion")
        return False
    else:
        print("✅ Clean Architecture VALIDADA")
        print()
        print("   ✓ Domain no depende de Infrastructure")
        print("   ✓ Dependency Inversion cumplido")
        print("   ✓ Arquitectura limpia mantenida")
        return True


def check_solid_violations():
    """
    Verifica principios SOLID básicos mediante análisis estático
    
    Nota del desarrollador:
    Este es un análisis básico. Para validación completa se requieren
    herramientas como SonarQube o análisis manual.
    """
    print()
    print("🔍 Validando principios SOLID...")
    print("=" * 60)

    src_path = Path("src")
    issues = []

    for python_file in src_path.rglob("*.py"):
        if python_file.name == "__init__.py":
            continue

        with open(python_file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=str(python_file))
            except SyntaxError:
                continue

        # Verificar tamaño de clases (Single Responsibility)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 15:
                    issues.append(
                        f"⚠️  {python_file.name}: Clase '{node.name}' tiene {len(methods)} métodos "
                        f"(posible violación de Single Responsibility)"
                    )

    if issues:
        print("⚠️  POSIBLES VIOLACIONES DE SOLID:")
        print()
        for issue in issues:
            print(f"  {issue}")
        print()
        print("Revisar manualmente estas clases")
        return True  # No falla CI, solo advierte
    else:
        print("✅ No se detectaron violaciones obvias de SOLID")
        return True


if __name__ == "__main__":
    architecture_valid = check_domain_imports()
    solid_check = check_solid_violations()

    print()
    print("=" * 60)

    if not architecture_valid:
        print("❌ VALIDACIÓN FALLIDA")
        sys.exit(1)
    else:
        print("✅ VALIDACIÓN EXITOSA")
        sys.exit(0)
