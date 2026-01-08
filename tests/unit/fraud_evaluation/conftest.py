"""
Pytest Configuration for fraud_evaluation tests
Shared fixtures and configuration
"""
import pytest
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))


@pytest.fixture
def sample_transaction_data():
    """Fixture con datos de transacción de ejemplo"""
    return {
        "id": "txn_test_001",
        "amount": 100.50,
        "user_id": "user_test_001",
        "location": {"latitude": 40.7128, "longitude": -74.0060},
        "timestamp": "2026-01-08T12:00:00Z",
    }


@pytest.fixture
def sample_high_amount_transaction():
    """Fixture con transacción de monto alto"""
    return {
        "id": "txn_test_002",
        "amount": 5000.00,
        "user_id": "user_test_001",
        "location": {"latitude": 40.7128, "longitude": -74.0060},
        "timestamp": "2026-01-08T12:00:00Z",
    }


@pytest.fixture
def sample_unusual_location_transaction():
    """Fixture con transacción de ubicación inusual"""
    return {
        "id": "txn_test_003",
        "amount": 100.00,
        "user_id": "user_test_001",
        "location": {
            "latitude": 34.0522,
            "longitude": -118.2437,
        },  # Los Angeles
        "timestamp": "2026-01-08T12:00:00Z",
    }
