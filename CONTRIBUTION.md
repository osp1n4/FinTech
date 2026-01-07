🤝 Guía de Contribución al Motor de Fraude

## 1. Flujo de Contribución

1.  Cree una rama de funcionalidad (`feature/nombre-de-la-hu` o `fix/issue-id`) desde la rama `develop`.
2.  Implemente siguiendo el ciclo **TDD/BDD**: Escribir test > Escribir código > Refactorizar.
3.  Asegúrese de que la cobertura de tests no baje del 70%.
4.  Cree un Pull Request (PR) a la rama `develop`.

## 2. Principios y Estándares de Código

* **Arquitectura Limpia:** Las dependencias deben ir de Infrastructure a Domain. Se prohíben las importaciones de `infrastructure` dentro de la capa `domain` (FT-007).
* **SOLID:** El código debe cumplir y no violar los principios SOLID.
* **Patrón Strategy:** Se implementa explícitamente el Patrón Strategy para manejar diferentes reglas de validación.

## 3. Directrices para Código Asistido por IA (FT-008)

**Regla del Crítico (Obligatorio):**
Por cada módulo importante generado o refactorizado por la IA, debe incluir un comentario obligatorio (`// HUMAN REVIEW: ...`) explicando qué mejoró de la sugerencia original.

## 4. Ejecución Local

Para levantar el entorno de desarrollo con los 5 servicios (API, Worker, MongoDB, Redis, RabbitMQ):
```bash
docker compose up --build