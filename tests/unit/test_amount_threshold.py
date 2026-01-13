from decimal import Decimal
from datetime import datetime
import pytest

from src.domain.strategies.amount_threshold import AmountThresholdStrategy
from src.domain.models import Transaction, Location


def make_transaction(amount: Decimal):
    return Transaction(
        id="t1",
        amount=amount,
        user_id="u1",
        location=Location(latitude=0.0, longitude=0.0),
        timestamp=datetime.now()
    )


def test_threshold_positive():
    with pytest.raises(ValueError):
        AmountThresholdStrategy(Decimal('0'))


def test_evaluate_below_threshold():
    strat = AmountThresholdStrategy(Decimal('1500.00'))
    tx = make_transaction(Decimal('100.00'))
    res = strat.evaluate(tx)
    assert res['risk_level'].name == 'LOW_RISK'
    assert res['reasons'] == []


def test_evaluate_above_threshold():
    strat = AmountThresholdStrategy(Decimal('1500.00'))
    tx = make_transaction(Decimal('2000.00'))
    res = strat.evaluate(tx)
    assert res['risk_level'].name == 'HIGH_RISK'
    assert 'amount_threshold_exceeded' in res['reasons']


def test_evaluate_with_none_transaction():
    strat = AmountThresholdStrategy(Decimal('100.00'))
    with pytest.raises(ValueError):
        strat.evaluate(None)
