from datetime import datetime
from decimal import Decimal
import pytest

from src.domain.models import (
    Location,
    Transaction,
    User,
    RiskLevel,
)


def test_location_validation():
    loc = Location(latitude=10.0, longitude=20.0)
    assert loc.latitude == pytest.approx(10.0)
    assert loc.longitude == pytest.approx(20.0)

    with pytest.raises(ValueError):
        Location(latitude=100.0, longitude=0.0)


def test_transaction_validation():
    loc = Location(latitude=0.0, longitude=0.0)
    with pytest.raises(ValueError):
        Transaction(id="", amount=Decimal('10.00'), user_id="u1", location=loc, timestamp=datetime.now())

    with pytest.raises(ValueError):
        Transaction(id="t1", amount=Decimal('0'), user_id="u1", location=loc, timestamp=datetime.now())


def test_user_validation():
    with pytest.raises(ValueError):
        User(user_id="ab", email="a@b.com", hashed_password="pw", full_name="Name")

    with pytest.raises(ValueError):
        User(user_id="user1", email="invalid-email", hashed_password="pw", full_name="Name")

    u = User(user_id="user1", email="user@example.com", hashed_password="pw", full_name="Full Name")
    assert u.is_active is True
    assert u.is_verified is False
