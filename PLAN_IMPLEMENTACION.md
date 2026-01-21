# 🏦 FinTech – Sistema de Autenticación Admin
## Plan de Implementación

**Arquitectura:** Microservicios + Event-Driven  


---
## 1️⃣ Fase 1 – Login para Admin Dashboard
**Objetivo:** Login para Admin Dashboard (localhost:3001) reutilizando arquitectura existente

## Paso 1 – Backend (Models + Repository)

### Objetivo
Crear entidad Admin y persistencia MongoDB.

### Actividades
- Crear `Admin` entity (models.py)
- Implementar `AdminRepository` con 8 métodos CRUD
- Configurar colección `admins` con índices únicos

### Metodología TDD
- **Red**: Tests fallan → Commit + Push
- **Green**: Implementar mínimo → Commit + Push
- **Refactor**: Optimizar → Commit + Push
- **Cobertura**: >70% en lógica de negocio

### Código Limpio y SOLID
- **S**: Admin solo representa administrador
- **O**: Extensible sin modificación
- **D**: Depende de abstracciones (pymongo)

### Entregables
- Admin entity funcional
- AdminRepository (save, find, exists, update)
- 26 tests unitarios (13 model + 13 repository)

---

## Paso 2 – Backend (Use Cases + API)

### Objetivo
Lógica de negocio y endpoints REST.

### Actividades
- Implementar 3 use cases:
  - RegisterAdminUseCase (validación + email verificación)
  - LoginAdminUseCase (JWT + verificación email)
  - VerifyAdminEmailUseCase (token 6 dígitos)
- Crear 4 endpoints REST en `admin_auth_routes.py`
- Integrar router en `main.py`

### Endpoints
- POST `/api/v1/admin/auth/register` (201)
- POST `/api/v1/admin/auth/login` (200)
- POST `/api/v1/admin/auth/verify-email` (200)
- GET `/api/v1/admin/auth/me` (200, protected)

### Metodología TDD
- **Red**: Tests integración HTTP fallan
- **Green**: Implementar endpoints
- **Refactor**: Optimizar error handling
- **Cobertura**: >70%

### Entregables
- 3 use cases funcionales
- 4 endpoints REST
- 14 tests unitarios + 9 tests integración

---

## Paso 3 – Frontend

### Objetivo
UI para login/registro/verificación.

### Actividades
- Crear 4 componentes React:
  - LoginPage (admin_id + password)
  - RegisterPage (form + validaciones)
  - VerifyEmailPage (código 6 dígitos)
  - ProtectedRoute (guard con localStorage)
- Configurar rutas en `App.tsx`

### Metodología TDD
- Tests vitest para validaciones frontend
- Integración con backend via fetch

### Entregables
- 4 páginas funcionales
- Rutas públicas y protegidas
- Navegación completa

---

## Paso 4 – Testing E2E y Documentación

### Objetivo
Validar flujo completo y documentar.

### Actividades
- Tests E2E con Playwright (6 tests)
- Crear `AUTH_FLOW_ADMIN.md` con diagramas
- Actualizar README
- Postman collection con 4 endpoints

### Entregables
- Tests E2E funcionales
- Documentación técnica
- Guía de uso

---

## 🧰 Stack Tecnológico

### Backend
- Python 3.11, FastAPI, MongoDB
- JWT, Bcrypt, SMTP

### Frontend
- React + TypeScript, Vite
- React Router, Tailwind CSS

### Testing
- pytest, pytest-cov, Playwright

### Herramientas
- Docker Compose, Git, Postman

---

## 📊 Métricas de Éxito

| Métrica | Objetivo | Estado |
|---------|----------|--------|
| Cobertura | >70% | ✅ |
| Tests Unitarios | 40+ | ✅ 40 |
| Tests Integración | 9+ | ✅ 9 |
| Tests E2E | 6+ | ⏳ |
| SOLID | 0 violaciones | ✅ |

---

## 📋 Principios Aplicados

### TDD
- Red → Green → Refactor
- Tests primero, cobertura >70%

### SOLID
- **S**: Single Responsibility
- **O**: Open/Closed
- **D**: Dependency Inversion

### Clean Code
- Nombres descriptivos
- Sin duplicación
- Commits atómicos

---

## 2️⃣ Fase 2 – Chatbot de Soporte FAQ para User App

**Objetivo:** Implementar un chatbot sencillo de preguntas frecuentes (FAQ) en la página principal del usuario, sin IA avanzada ni servicios externos.

---

## Paso 1 – Configuración FAQ (Data Layer)

### Objetivo
Crear estructura de datos para preguntas frecuentes contextualizadas al flujo FinTech.

### Actividades
- Crear archivo `faqData.ts` con preguntas y respuestas
- Implementar interfaz `FAQItem` tipada
- Organizar FAQs por categorías
- Crear utilidad `faqMatcher.ts` para búsqueda por keywords

### Metodología TDD
- **Red**: Tests para matcher de keywords fallan → Commit + Push
- **Green**: Implementar lógica de matching → Commit + Push
- **Refactor**: Optimizar algoritmo de búsqueda → Commit + Push
- **Cobertura**: >70% en lógica de matching

### Código Limpio y SOLID
- **S**: Cada módulo tiene una responsabilidad (data, matching, UI)
- **O**: FAQs extensibles sin modificar lógica
- **D**: Componentes dependen de interfaces, no implementaciones

### Entregables
- `faqData.ts` con 15+ preguntas organizadas
- `faqMatcher.ts` con lógica de búsqueda
- 8 tests unitarios para matcher

### FAQs Contextualizadas FinTech

#### 🔐 Cuenta y Acceso
| Pregunta | Respuesta |
|----------|-----------|
| ¿Cómo creo una cuenta? | Para crear una cuenta, haz clic en "Registrarse", ingresa tu email, user_id y contraseña. Recibirás un código de 6 dígitos para verificar tu email. |
| ¿Cómo inicio sesión? | Ingresa tu user_id y contraseña en la página de login. Si tu email está verificado, accederás al dashboard. |
| Olvidé mi contraseña | Contacta a soporte técnico para restablecer tu contraseña de forma segura al siguiente número 3604050 ext 101. |
| ¿Cómo verifico mi email? | Después del registro, recibirás un código de 6 dígitos. Ingrésalo en la página de verificación. |

#### 💳 Transacciones
| Pregunta | Respuesta |
|----------|-----------|
| ¿Cómo realizo una transacción? | Desde el dashboard, selecciona "Nueva Transacción", ingresa el monto y destino. El sistema evaluará automáticamente el riesgo. |
| ¿Qué significa el estado de mi transacción? | APPROVED = aprobada, PENDING = en revisión, REJECTED = rechazada por riesgo alto. |
| ¿Por qué mi transacción fue rechazada? | Las transacciones se rechazan si el nivel de riesgo es HIGH_RISK. Puede ser por monto alto, horario inusual o ubicación sospechosa. |
| ¿Cómo veo mi historial de transacciones? | En el dashboard principal encontrarás la lista de tus transacciones recientes con su estado y nivel de riesgo. |

#### 🛡️ Seguridad y Fraude
| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué es el nivel de riesgo? | Es una evaluación automática: LOW_RISK (segura), MEDIUM_RISK (requiere atención), HIGH_RISK (bloqueada). |
| ¿Cómo reporto una transacción sospechosa? | Contacta inmediatamente a soporte con el ID de la transacción. Bloquearemos tu cuenta preventivamente. |
| ¿Por qué se bloqueó mi transacción? | El sistema detectó patrones inusuales: monto muy alto, horario nocturno, ubicación diferente o transacciones muy rápidas. |
| ¿Qué reglas evalúan mis transacciones? | Evaluamos: monto (>$10,000), horario (11pm-6am), ubicación GPS, velocidad entre transacciones y dispositivo. |

#### ⚠️ Problemas Técnicos
| Pregunta | Respuesta |
|----------|-----------|
| La página no carga | Verifica tu conexión a internet y recarga la página. Si persiste, limpia la caché del navegador. |
| Veo un error en pantalla | Toma una captura del error y repórtalo a soporte con el código mostrado. |
| No puedo completar una acción | Cierra sesión, espera 30 segundos y vuelve a intentar. Si continúa, contacta soporte. |

#### 📞 Soporte
| Pregunta | Respuesta |
|----------|-----------|
| ¿Cómo contacto a soporte humano? | Envía un email a soporte@fintech.com |
| ¿En qué horarios atiende soporte? | Lunes a Viernes de 8:00 AM a 6:00 PM. Emergencias de fraude: 24/7. |

---

## Paso 2 – Componentes UI (Presentation Layer)

### Objetivo
Crear componentes React para el chatbot con diseño UX amigable.

### Actividades
- Crear `ChatButton.tsx` (botón flotante 💬)
- Crear `ChatModal.tsx` (panel de chat)
- Crear `ChatMessage.tsx` (burbuja de mensaje)
- Crear `FAQList.tsx` (lista de preguntas sugeridas)
- Crear `ChatInput.tsx` (campo de entrada)

### Metodología TDD
- **Red**: Tests de renderizado fallan → Commit + Push
- **Green**: Implementar componentes → Commit + Push
- **Refactor**: Extraer estilos y optimizar → Commit + Push
- **Cobertura**: >70%

### Diseño UX
- Botón flotante en esquina inferior derecha
- Modal con animación suave
- Mensajes con timestamps
- Indicador "Bot automático" visible
- Scroll automático a último mensaje

### Entregables
- 5 componentes React funcionales
- Estilos Tailwind CSS
- 10 tests unitarios (2 por componente)

---

## Paso 3 – Lógica de Chat (Business Logic)

### Objetivo
Implementar hook personalizado y lógica de conversación.

### Actividades
- Crear `useChatbot.ts` hook con estado del chat
- Implementar lógica de respuestas automáticas
- Manejar flujo de conversación
- Agregar respuesta fallback para no coincidencias

### Metodología TDD
- **Red**: Tests del hook fallan → Commit + Push
- **Green**: Implementar estado y handlers → Commit + Push
- **Refactor**: Optimizar re-renders → Commit + Push
- **Cobertura**: >70%

### Flujo de Conversación
```
1. Usuario abre chat
2. Bot: "Hola 👋, soy el asistente de Soporte FinTech. ¿En qué puedo ayudarte?"
3. Usuario selecciona FAQ o escribe pregunta
4. Bot busca coincidencia por keywords
5. Si hay match → Responde con FAQ
6. Si no hay match → "No encontré una respuesta. ¿Deseas hablar con soporte humano?"
7. Usuario puede continuar o cerrar
```

### Entregables
- `useChatbot.ts` hook completo
- Tipos TypeScript definidos
- 6 tests unitarios para hook

---

## Paso 4 – Integración y Testing

### Objetivo
Integrar chatbot en HomePage y validar funcionamiento completo.

### Actividades
- Integrar `ChatButton` en `HomePage.tsx`
- Conectar componentes con hook
- Agregar persistencia en localStorage (opcional)
- Tests E2E con Playwright

### Metodología TDD
- **Red**: Tests E2E fallan → Commit + Push
- **Green**: Integrar y corregir → Commit + Push
- **Refactor**: Optimizar performance → Commit + Push
- **Cobertura**: >70%

### Tests E2E
1. Abrir y cerrar chat modal
2. Seleccionar pregunta de lista FAQ
3. Escribir pregunta y recibir respuesta
4. Pregunta sin coincidencia muestra fallback
5. Scroll automático funciona
6. Chat persiste al recargar (opcional)

### Entregables
- Chatbot integrado en producción
- 6 tests E2E funcionales
- Documentación de uso

---

## 🧰 Stack Tecnológico Fase 2

### Frontend
- React 18 + TypeScript
- Tailwind CSS (estilos)
- Vite (build tool)

### Testing
- Vitest (unit tests)
- React Testing Library
- Playwright (E2E)

### Herramientas
- ESLint + Prettier
- Git (commits atómicos)

---

## 📊 Métricas de Éxito Fase 2

| Métrica | Objetivo | Estado |
|---------|----------|--------|
| Cobertura | >70% | ✅ 98.43% |
| Tests Unitarios | 24+ | ✅ 62 |
| Tests E2E | 6+ | ⏳ |
| FAQs implementadas | 15+ | ✅ 17 |
| Componentes | 5 | ✅ 5 |
| SOLID | 0 violaciones | ✅ |

---

## 📁 Estructura de Archivos

```
frontend/user-app/src/
├── components/
│   └── chatbot/
│       ├── ChatButton.tsx       # Botón flotante
│       ├── ChatModal.tsx        # Panel principal
│       ├── ChatMessage.tsx      # Burbuja de mensaje
│       ├── ChatInput.tsx        # Campo de entrada
│       ├── FAQList.tsx          # Lista de sugerencias
│       └── index.ts             # Barrel export
├── hooks/
│   └── useChatbot.ts            # Hook de lógica
├── data/
│   └── faqData.ts               # Preguntas y respuestas
├── utils/
│   └── faqMatcher.ts            # Lógica de matching
└── types/
    └── chatbot.types.ts         # Interfaces TypeScript
```

---

## 🔄 Flujo de Commits TDD

### Paso 1 - FAQ Data
```bash
# RED
git commit -m "test(chatbot): add failing tests for FAQ matcher"
git push

# GREEN  
git commit -m "feat(chatbot): implement FAQ data and matcher"
git push

# REFACTOR
git commit -m "refactor(chatbot): optimize keyword matching algorithm"
git push
```

### Paso 2 - Componentes UI
```bash
# RED
git commit -m "test(chatbot): add failing tests for chat components"
git push

# GREEN
git commit -m "feat(chatbot): implement ChatButton and ChatModal"
git push

# REFACTOR
git commit -m "refactor(chatbot): extract reusable styles"
git push
```

### Paso 3 - Hook
```bash
# RED
git commit -m "test(chatbot): add failing tests for useChatbot hook"
git push

# GREEN
git commit -m "feat(chatbot): implement useChatbot with conversation flow"
git push

# REFACTOR
git commit -m "refactor(chatbot): optimize state management"
git push
```

### Paso 4 - Integración
```bash
# RED
git commit -m "test(e2e): add failing E2E tests for chatbot"
git push

# GREEN
git commit -m "feat(chatbot): integrate chatbot in HomePage"
git push

# REFACTOR
git commit -m "refactor(chatbot): final cleanup and documentation"
git push
```

---

## 📋 Checklist de Implementación

### Paso 1 - Data Layer ✅ COMPLETADO
- [x] Crear `chatbot.types.ts` con interfaces
- [x] Crear `faqData.ts` con 17 FAQs
- [x] Crear `faqMatcher.ts` con lógica
- [x] 32 tests unitarios passing
- [x] Cobertura 97%

### Paso 2 - UI Components ✅ COMPLETADO
- [x] `ChatButton.tsx` implementado
- [x] `ChatModal.tsx` implementado
- [x] `ChatMessage.tsx` implementado
- [x] `ChatInput.tsx` implementado
- [x] `FAQList.tsx` implementado
- [x] 30 tests unitarios passing
- [x] Estilos Tailwind aplicados
- [x] Cobertura 98.43%

### Paso 3 - Business Logic
- [ ] `useChatbot.ts` hook completo
- [ ] Flujo de conversación funcional
- [ ] Fallback para no coincidencias
- [ ] 6 tests unitarios passing

### Paso 4 - Integration
- [ ] Chatbot visible en HomePage
- [ ] 6 tests E2E passing
- [ ] Documentación actualizada
- [ ] PR creado y revisado
