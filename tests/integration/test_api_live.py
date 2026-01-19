"""
Tests de integración contra el API en ejecución (Docker).

Estos tests validan el flujo completo de la aplicación
ejecutándose en contenedores Docker.
"""
import pytest
import requests
import time

API_BASE_URL = "http://localhost:8000"


def wait_for_api(max_retries=5, delay=2):
    """Espera a que el API esté disponible."""
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(delay)
    return False


@pytest.fixture(scope="session", autouse=True)
def check_api_available():
    """Verifica que el API esté disponible antes de ejecutar los tests."""
    if not wait_for_api():
        pytest.skip("API no disponible en http://localhost:8000")


class TestTransactionEndpointsLive:
    """Tests de integración para endpoints de transacciones (API en vivo)."""
    
    def test_validate_transaction_endpoint_exists(self):
        """Test: El endpoint POST /api/v1/transaction/validate debe existir."""
        # Arrange
        transaction_data = {
            "userId": "integration_test_001",
            "amount": 100.0,
            "location": "4.7110,-74.0721",
            "deviceId": "test_device_001"
        }
        
        # Act
        response = requests.post(
            f"{API_BASE_URL}/api/v1/transaction/validate",
            json=transaction_data,
            timeout=10
        )
        
        # Assert
        assert response.status_code in [200, 201], f"Status code: {response.status_code}, Response: {response.text}"
    
    def test_validate_transaction_low_risk(self):
        """Test: Transacción de bajo monto debe ser procesada."""
        # Arrange
        transaction_data = {
            "userId": "integration_test_002",
            "amount": 100.0,  # Monto bajo
            "location": "4.7110,-74.0721",
            "deviceId": "test_device_002"
        }
        
        # Act
        response = requests.post(
            f"{API_BASE_URL}/api/v1/transaction/validate",
            json=transaction_data,
            timeout=10
        )
        
        # Assert
        assert response.status_code in [200, 201]
        data = response.json()
        assert "status" in data
        assert "transactionId" in data
        print(f"✓ Transacción procesada: {data.get('status')}, Risk: {data.get('riskLevel')}")
    
    def test_validate_transaction_high_risk(self):
        """Test: Transacción de alto monto debe ser marcada como alto riesgo."""
        # Arrange
        transaction_data = {
            "userId": "integration_test_003",
            "amount": 5000.0,  # Monto alto (>1500)
            "location": "4.7110,-74.0721",
            "deviceId": "test_device_003"
        }
        
        # Act
        response = requests.post(
            f"{API_BASE_URL}/api/v1/transaction/validate",
            json=transaction_data,
            timeout=10
        )
        
        # Assert
        assert response.status_code in [200, 201]
        data = response.json()
        assert "status" in data
        assert "riskLevel" in data
        # Verificar que se detectó el alto riesgo
        assert data.get("riskLevel") == "HIGH_RISK" or data.get("riskScore", 0) > 50
        print(f"✓ Alto riesgo detectado: {data.get('riskLevel')}, Score: {data.get('riskScore')}")
    
    def test_validate_transaction_missing_fields(self):
        """Test: Debe rechazar transacción con campos faltantes."""
        # Arrange
        incomplete_data = {
            "userId": "integration_test_004"
            # Faltan amount, location
        }
        
        # Act
        response = requests.post(
            f"{API_BASE_URL}/api/v1/transaction/validate",
            json=incomplete_data,
            timeout=10
        )
        
        # Assert
        assert response.status_code == 422  # Unprocessable Entity
        print(f"✓ Validación correcta: campos faltantes rechazados")
    
    def test_validate_transaction_device_validation(self):
        """Test: Debe validar dispositivos nuevos vs conocidos."""
        # Arrange - Primera transacción con dispositivo nuevo
        transaction_data = {
            "userId": "integration_test_005",
            "amount": 200.0,
            "location": "4.7110,-74.0721",
            "deviceId": "brand_new_device_123"
        }
        
        # Act
        response = requests.post(
            f"{API_BASE_URL}/api/v1/transaction/validate",
            json=transaction_data,
            timeout=10
        )
        
        # Assert
        assert response.status_code in [200, 201]
        data = response.json()
        # Un dispositivo nuevo puede incrementar el riesgo
        assert "violations" in data or "riskScore" in data
        print(f"✓ Validación de dispositivo: Risk={data.get('riskLevel')}, Violations={data.get('violations')}")


class TestAdminEndpointsLive:
    """Tests de integración para endpoints del admin (API en vivo)."""
    
    def test_get_metrics_endpoint_exists(self):
        """Test: El endpoint GET /api/v1/admin/metrics debe existir."""
        # Act
        response = requests.get(f"{API_BASE_URL}/api/v1/admin/metrics", timeout=10)
        
        # Assert
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Métricas obtenidas: {list(data.keys())}")
    
    def test_get_transactions_log_endpoint_exists(self):
        """Test: El endpoint GET /api/v1/admin/transactions/log debe existir."""
        # Act
        response = requests.get(f"{API_BASE_URL}/api/v1/admin/transactions/log", timeout=10)
        
        # Assert
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Log de transacciones: {len(data.get('transactions', []))} transacciones")
    
    def test_get_rules_endpoint_exists(self):
        """Test: El endpoint GET /api/v1/admin/rules debe existir."""
        # Act
        response = requests.get(f"{API_BASE_URL}/api/v1/admin/rules", timeout=10)
        
        # Assert
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Reglas configuradas: {len(data.get('rules', []))} reglas")


class TestHealthCheckLive:
    """Tests para el endpoint de health check (API en vivo)."""
    
    def test_health_check_endpoint(self):
        """Test: El endpoint de health check debe retornar status OK."""
        # Act
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "version" in data
        print(f"✓ Health check OK: {data.get('status')}, Version: {data.get('version')}")


class TestUserEndpointsLive:
    """Tests de integración para endpoints de usuario (API en vivo)."""
    
    def test_get_user_transactions(self):
        """Test: El endpoint GET /api/v1/user/transactions/{user_id} debe existir."""
        # Act
        response = requests.get(f"{API_BASE_URL}/api/v1/user/transactions/ospina12", timeout=10)
        
        # Assert
        assert response.status_code in [200, 401, 404]
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Transacciones de usuario obtenidas: {len(data) if isinstance(data, list) else 'N/A'}")
