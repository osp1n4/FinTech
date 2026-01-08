import { Page, APIRequestContext, expect } from '@playwright/test';

/**
 * ValidateTransaction - Task para validar transacciones vía API
 * Patrón Screenplay: Encapsula la lógica de validación de transacciones
 */
export class ValidateTransaction {
  /**
   * Crear y validar transacción vía API
   */
  static async viaAPI(
    request: APIRequestContext,
    transactionData: {
      userId: string;
      amount: number;
      location: string;
      deviceId: string;
    }
  ): Promise<{
    transactionId: string;
    status: string;
    riskScore: number;
  }> {
    const response = await request.post('http://localhost:8000/api/v1/transaction/validate', {
      data: transactionData
    });

    expect(response.status()).toBe(200);
    
    const responseData = await response.json();
    
    return {
      transactionId: responseData.transactionId,  // Backend usa camelCase
      status: responseData.status,
      riskScore: responseData.riskScore || 0
    };
  }

  /**
   * Validar transacción de bajo riesgo
   */
  static async lowRisk(
    request: APIRequestContext,
    userId: string = 'user_test_001'
  ): Promise<string> {
    const result = await this.viaAPI(request, {
      userId,
      amount: 50.0,
      location: '4.7110,-74.0721', // Bogotá
      deviceId: 'device_known_001'
    });
    
    return result.transactionId;
  }

  /**
   * Validar transacción de alto riesgo (monto alto)
   */
  static async highRiskAmount(
    request: APIRequestContext,
    userId: string = 'user_test_001'
  ): Promise<string> {
    const result = await this.viaAPI(request, {
      userId,
      amount: 5000.0, // Monto muy alto
      location: '4.7110,-74.0721',
      deviceId: 'device_known_001'
    });
    
    return result.transactionId;
  }

  /**
   * Validar transacción con ubicación sospechosa
   */
  static async suspiciousLocation(
    request: APIRequestContext,
    userId: string = 'user_test_001'
  ): Promise<string> {
    const result = await this.viaAPI(request, {
      userId,
      amount: 100.0,
      location: '40.7128,-74.0060', // Nueva York (muy lejos de Bogotá)
      deviceId: 'device_known_001'
    });
    
    return result.transactionId;
  }

  /**
   * Validar transacción con dispositivo desconocido
   */
  static async unknownDevice(
    request: APIRequestContext,
    userId: string = 'user_test_001'
  ): Promise<string> {
    const result = await this.viaAPI(request, {
      userId,
      amount: 100.0,
      location: '4.7110,-74.0721',
      deviceId: 'device_unknown_999' // Dispositivo no registrado
    });
    
    return result.transactionId;
  }

  /**
   * Verificar estado de transacción vía API
   */
  static async checkStatus(
    request: APIRequestContext,
    transactionId: string
  ): Promise<{
    status: string;
    riskScore: number;
  }> {
    const response = await request.get(`http://localhost:8000/api/v1/transaction/${transactionId}`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    
    return {
      status: data.status,
      riskScore: data.risk_score || 0
    };
  }

  /**
   * Obtener historial de transacciones de usuario vía API
   */
  static async getUserHistory(
    request: APIRequestContext,
    userId: string
  ): Promise<Array<any>> {
    const response = await request.get(`http://localhost:8000/api/v1/user/${userId}/transactions`);
    
    expect(response.status()).toBe(200);
    
    return await response.json();
  }
}
