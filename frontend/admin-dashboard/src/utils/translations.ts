/**
 * Traduce los nombres de las violaciones del inglés al español
 */

const violationTranslations: Record<string, string> = {
  // Transacciones rápidas
  'rapid_transactions_detected': 'Límite de transacciones alcanzado',
  'approaching_transaction_limit': 'Aproximándose al límite de transacciones',
  
  // Monto
  'amount_threshold_exceeded': 'Monto excede el umbral permitido',
  'high_amount_transaction': 'Transacción de monto elevado',
  
  // Ubicación
  'unusual_location': 'Ubicación inusual o sospechosa',
  'no_historical_location': 'Sin historial de ubicación',
  'location_mismatch': 'Ubicación no coincide con el patrón habitual',
  
  // Dispositivo
  'Dispositivo nuevo o no reconocido': 'Dispositivo nuevo o no reconocido',
  'unknown_device': 'Dispositivo no reconocido',
  'new_device': 'Dispositivo nuevo',
  
  // Tiempo
  'unusual_time': 'Horario inusual de transacción',
  'unusual_time_pattern': 'Patrón de tiempo inusual',
  
  // Otros
  'suspicious_pattern': 'Patrón sospechoso detectado',
  'multiple_risk_factors': 'Múltiples factores de riesgo',
};

/**
 * Traduce una violación al español
 * @param violation - Nombre de la violación en inglés
 * @returns Nombre de la violación en español
 */
export function translateViolation(violation: string): string {
  // Si ya está en español, retornar tal cual
  if (violationTranslations[violation]) {
    return violationTranslations[violation];
  }
  
  // Si no está en el diccionario, formatear el texto
  // Convertir snake_case a palabras separadas y capitalizar
  return violation
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Traduce un array de violaciones
 * @param violations - Array de violaciones en inglés
 * @returns Array de violaciones en español
 */
export function translateViolations(violations: string[]): string[] {
  return violations.map(translateViolation);
}
