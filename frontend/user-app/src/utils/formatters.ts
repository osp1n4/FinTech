/**
 * Formatea un número como moneda USD
 */
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

/**
 * Genera un ID de usuario aleatorio
 */
export const generateUserId = (): string => {
  // Usar crypto.getRandomValues para generar número seguro
  const randomNum = crypto.getRandomValues(new Uint32Array(1))[0] % 100000;
  return `user_${randomNum}`;
};

/**
 * Obtiene o genera un ID de dispositivo persistente por usuario
 * El deviceId se guarda en localStorage por usuario para mantener consistencia
 * entre transacciones del mismo usuario/dispositivo
 * @param userId - ID del usuario actual
 */
export const generateDeviceId = (userId: string): string => {
  const STORAGE_KEY = `fraud_detection_device_id_${userId}`;
  
  // Intentar obtener el deviceId existente para este usuario
  let deviceId = localStorage.getItem(STORAGE_KEY);
  
  // Si no existe, generar uno nuevo y guardarlo
  if (!deviceId) {
    const devices = ['mobile', 'tablet', 'desktop'];
    const randomIndex = crypto.getRandomValues(new Uint32Array(1))[0] % devices.length;
    const randomDevice = devices[randomIndex];
    const randomId = crypto.randomUUID().substring(0, 6).toUpperCase();
    deviceId = `${randomDevice}_${randomId}`;
    
    // Guardar en localStorage para futuras transacciones de este usuario
    localStorage.setItem(STORAGE_KEY, deviceId);
  }
  
  return deviceId;
};
