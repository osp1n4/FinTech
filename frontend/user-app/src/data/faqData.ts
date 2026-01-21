/**
 * FAQ Data - Preguntas frecuentes FinTech
 * Fase 2 - Paso 1: Data Layer
 * 
 * Implementación GREEN - Datos de FAQs contextualizadas
 */

import type { FAQItem } from '../types/chatbot.types';

/**
 * Lista de preguntas frecuentes contextualizadas para FinTech
 */
export const faqData: FAQItem[] = [
  // 🔐 Cuenta y Acceso
  {
    id: 'faq-cuenta-1',
    category: 'cuenta-acceso',
    question: '¿Cómo creo una cuenta?',
    answer: 'Para crear una cuenta, haz clic en "Registrarse", ingresa tu email, user_id y contraseña. Recibirás un código de 6 dígitos para verificar tu email.',
    keywords: ['crear', 'cuenta', 'registrar', 'registro', 'nueva', 'usuario']
  },
  {
    id: 'faq-cuenta-2',
    category: 'cuenta-acceso',
    question: '¿Cómo inicio sesión?',
    answer: 'Ingresa tu user_id y contraseña en la página de login. Si tu email está verificado, accederás al dashboard.',
    keywords: ['iniciar', 'sesion', 'login', 'entrar', 'acceder', 'ingresar']
  },
  {
    id: 'faq-cuenta-3',
    category: 'cuenta-acceso',
    question: 'Olvidé mi contraseña',
    answer: 'Contacta a soporte técnico para restablecer tu contraseña de forma segura al siguiente número 3604050 ext 101.',
    keywords: ['olvide', 'contraseña', 'password', 'recuperar', 'restablecer', 'olvidé']
  },
  {
    id: 'faq-cuenta-4',
    category: 'cuenta-acceso',
    question: '¿Cómo verifico mi email?',
    answer: 'Después del registro, recibirás un código de 6 dígitos. Ingrésalo en la página de verificación.',
    keywords: ['verificar', 'email', 'correo', 'codigo', 'verificacion', 'confirmar']
  },

  // 💳 Transacciones
  {
    id: 'faq-trans-1',
    category: 'transacciones',
    question: '¿Cómo realizo una transacción?',
    answer: 'Desde el dashboard, selecciona "Nueva Transacción", ingresa el monto y destino. El sistema evaluará automáticamente el riesgo.',
    keywords: ['transaccion', 'realizar', 'hacer', 'enviar', 'transferir', 'pago']
  },
  {
    id: 'faq-trans-2',
    category: 'transacciones',
    question: '¿Qué significa el estado de mi transacción?',
    answer: 'APPROVED = aprobada, PENDING = en revisión, REJECTED = rechazada por riesgo alto.',
    keywords: ['estado', 'transaccion', 'approved', 'pending', 'rejected', 'significa']
  },
  {
    id: 'faq-trans-3',
    category: 'transacciones',
    question: '¿Por qué mi transacción fue rechazada?',
    answer: 'Las transacciones se rechazan si el nivel de riesgo es HIGH_RISK. Puede ser por monto alto, horario inusual o ubicación sospechosa.',
    keywords: ['rechazada', 'rechazo', 'porque', 'motivo', 'razon', 'bloqueo']
  },
  {
    id: 'faq-trans-4',
    category: 'transacciones',
    question: '¿Cómo veo mi historial de transacciones?',
    answer: 'En el dashboard principal encontrarás la lista de tus transacciones recientes con su estado y nivel de riesgo.',
    keywords: ['historial', 'transacciones', 'ver', 'lista', 'recientes', 'movimientos']
  },

  // 🛡️ Seguridad y Fraude
  {
    id: 'faq-seg-1',
    category: 'seguridad-fraude',
    question: '¿Qué es el nivel de riesgo?',
    answer: 'Es una evaluación automática: LOW_RISK (segura), MEDIUM_RISK (requiere atención), HIGH_RISK (bloqueada).',
    keywords: ['riesgo', 'nivel', 'seguridad', 'evaluacion', 'fraude', 'que']
  },
  {
    id: 'faq-seg-2',
    category: 'seguridad-fraude',
    question: '¿Cómo reporto una transacción sospechosa?',
    answer: 'Contacta inmediatamente a soporte con el ID de la transacción. Bloquearemos tu cuenta preventivamente.',
    keywords: ['reportar', 'sospechosa', 'fraude', 'denuncia', 'alertar', 'reporto']
  },
  {
    id: 'faq-seg-3',
    category: 'seguridad-fraude',
    question: '¿Por qué se bloqueó mi transacción?',
    answer: 'El sistema detectó patrones inusuales: monto muy alto, horario nocturno, ubicación diferente o transacciones muy rápidas.',
    keywords: ['bloqueo', 'bloqueada', 'detenida', 'porque', 'razon', 'motivo']
  },
  {
    id: 'faq-seg-4',
    category: 'seguridad-fraude',
    question: '¿Qué reglas evalúan mis transacciones?',
    answer: 'Evaluamos: monto (>$10,000), horario (11pm-6am), ubicación GPS, velocidad entre transacciones y dispositivo.',
    keywords: ['reglas', 'evaluan', 'criterios', 'validacion', 'deteccion', 'filtros']
  },

  // ⚠️ Problemas Técnicos
  {
    id: 'faq-tech-1',
    category: 'problemas-tecnicos',
    question: 'La página no carga',
    answer: 'Verifica tu conexión a internet y recarga la página. Si persiste, limpia la caché del navegador.',
    keywords: ['pagina', 'carga', 'lenta', 'error', 'blanca', 'no']
  },
  {
    id: 'faq-tech-2',
    category: 'problemas-tecnicos',
    question: 'Veo un error en pantalla',
    answer: 'Toma una captura del error y repórtalo a soporte con el código mostrado.',
    keywords: ['error', 'pantalla', 'mensaje', 'falla', 'bug', 'problema']
  },
  {
    id: 'faq-tech-3',
    category: 'problemas-tecnicos',
    question: 'No puedo completar una acción',
    answer: 'Cierra sesión, espera 30 segundos y vuelve a intentar. Si continúa, contacta soporte.',
    keywords: ['completar', 'accion', 'funciona', 'boton', 'click', 'atascado']
  },

  // 📞 Soporte
  {
    id: 'faq-soporte-1',
    category: 'soporte',
    question: '¿Cómo contacto a soporte humano?',
    answer: 'Envía un email a soporte@fintech.com o escribe "hablar con humano" en este chat.',
    keywords: ['soporte', 'contactar', 'humano', 'ayuda', 'email', 'persona']
  },
  {
    id: 'faq-soporte-2',
    category: 'soporte',
    question: '¿En qué horarios atiende soporte?',
    answer: 'Lunes a Viernes de 8:00 AM a 6:00 PM. Emergencias de fraude: 24/7.',
    keywords: ['horario', 'atencion', 'soporte', 'horas', 'disponible', 'cuando']
  }
];

/**
 * Mensaje de bienvenida del bot
 */
export const WELCOME_MESSAGE = 'Hola 👋, soy el asistente de Soporte FinTech. ¿En qué puedo ayudarte?';

/**
 * Mensaje cuando no se encuentra coincidencia
 */
export const FALLBACK_MESSAGE = 'No encontré una respuesta para tu consulta. ¿Deseas hablar con soporte humano? Escribe "hablar con humano" o envía un email a soporte@fintech.com';
