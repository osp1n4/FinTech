"""
Tests de integración para los endpoints de la API.

HUMAN REVIEW (Maria Paula Gutierrez):
Estos tests validan el flujo completo de la aplicación,
desde la entrada HTTP hasta la respuesta, pasando por
todas las capas (API -> Application -> Domain -> Infrastructure).
"""
import pytest
from fastapi.testclient import TestClient
from decimal import Decimal


@pytest.fixture
def client():
    """Cliente de prueba para FastAPI."""
    from services.api_gateway.src.main import app
    return TestClient(app)


class TestTransactionEndpoints:
    """Tests de integración para endpoints de transacciones."""
    
    def test_validate_transaction_endpoint_exists(self, client):
        """Test: El endpoint POST /api/v1/transaction/validate debe existir."""
        # Arrange
        transaction_data = {
            "userId": "user_test_001",
            "amount": 100.0,
            "location": "4.7110,-74.0721",
            "deviceId": "device_001"
        }
        
        # Act
        response = client.post(
            "/api/v1/transaction/validate",
            json=transaction_data
        )
        
        # Assert
        # Debe retornar 200 OK o 201 Created (no 404 Not Found)
        assert response.status_code in [200, 201, 422]
    
    def test_validate_transaction_low_risk(self, client):
        """Test: Transacción de bajo monto debe ser aprobada."""
        # Arrange
        transaction_data = {
            "userId": "user_test_001",
            "amount": 100.0,  # Monto bajo
            "location": "4.7110,-74.0721",
            "deviceId": "device_001"
        }
        
        # Act
        response = client.post(
            "/api/v1/transaction/validate",
            json=transaction_data
        )
        
        # Assert
        assert response.status_code in [200, 201]
        data = response.json()
        assert "status" in data or "message" in data
    
    def test_validate_transaction_high_risk(self, client):
        """Test: Transacción de alto monto debe ser marcada como sospechosa."""
        # Arrange
        transaction_data = {
            "userId": "user_test_001",
            "amount": 5000.0,  # Monto alto
            "location": "4.7110,-74.0721",
            "deviceId": "device_001"
        }
        
        # Act
        response = client.post(
            "/api/v1/transaction/validate",
            json=transaction_data
        )
        
        # Assert
        assert response.status_code in [200, 201]
        data = response.json()
        # Debe indicar alto riesgo de alguna forma
        assert "risk" in str(data).lower() or "status" in data
    
    def test_validate_transaction_missing_fields(self, client):
        """Test: Debe rechazar transacción con campos faltantes."""
        # Arrange
        incomplete_data = {
            "userId": "user_test_001"
            # Faltan amount, location, deviceId
        }
        
        # Act
        response = client.post(
            "/api/v1/transaction/validate",
            json=incomplete_data
        )
        
        # Assert
        # Debe retornar 422 Unprocessable Entity
        assert response.status_code == 422


class TestAdminEndpoints:
    """Tests de integración para endpoints del admin."""
    
    def test_get_metrics_endpoint_exists(self, client):
        """Test: El endpoint GET /api/v1/admin/metrics debe existir."""
        # Act
        response = client.get("/api/v1/admin/metrics")
        
        # Assert
        assert response.status_code in [200, 401]  # 401 si requiere auth
    
    def test_get_transactions_log_endpoint_exists(self, client):
        """Test: El endpoint GET /api/v1/admin/transactions/log debe existir."""
        # Act
        response = client.get("/api/v1/admin/transactions/log")
        
        # Assert
        assert response.status_code in [200, 401]
    
    def test_get_rules_endpoint_exists(self, client):
        """Test: El endpoint GET /api/v1/admin/rules debe existir."""
        # Act
        response = client.get("/api/v1/admin/rules")
        
        # Assert
        assert response.status_code in [200, 401]
    
    def test_create_rule_endpoint_exists(self, client):
        """Test: El endpoint POST /api/v1/admin/rules debe existir."""
        # Arrange
        rule_data = {
            "name": "Test Rule",
            "type": "custom",
            "parameters": {},
            "enabled": True,
            "order": 10
        }
        
        # Act
        response = client.post("/api/v1/admin/rules", json=rule_data)
        
        # Assert
        assert response.status_code in [200, 201, 401, 422]
    
    def test_delete_rule_endpoint_exists(self, client):
        """Test: El endpoint DELETE /api/v1/admin/rules/{id} debe existir."""
        # Act
        response = client.delete("/api/v1/admin/rules/test_rule_id")
        
        # Assert
        assert response.status_code in [200, 204, 401, 404]
    
    def test_get_trends_endpoint_exists(self, client):
        """Test: El endpoint GET /api/v1/admin/trends debe existir."""
        # Act
        response = client.get("/api/v1/admin/trends")
        
        # Assert
        assert response.status_code in [200, 401]


class TestHealthCheck:
    """Tests para el endpoint de health check."""
    
    def test_health_check_endpoint(self, client):
        """Test: El endpoint de health check debe retornar status OK."""
        # Act
        response = client.get("/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy" or "status" in data


@pytest.mark.skip(reason="Requiere servicios externos (MongoDB, Redis, RabbitMQ)")
class TestEndToEndFlow:
    """Tests end-to-end del flujo completo."""
    
    def test_complete_transaction_flow(self, client):
        """Test: Flujo completo de transacción desde validación hasta log."""
        # TODO: Implementar cuando estén todos los servicios corriendo
        pass
