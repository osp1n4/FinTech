from datetime import datetime, timedelta
from decimal import Decimal
import pytest

from src.domain.strategies.rapid_transaction import RapidTransactionStrategy
from src.domain.models import Transaction, Location, RiskLevel


class DummyRedis:
    def __init__(self):
        self.store = {}

    def zadd(self, key, mapping):
        if key not in self.store:
            self.store[key] = {}
        self.store[key].update(mapping)

    def expire(self, key, seconds):
        # no-op for dummy
        pass

    def zremrangebyscore(self, key, min_score, max_score):
        """
        Simula el comportamiento de Redis:
        Elimina los elementos cuyo score está ENTRE min_score y max_score (inclusive).
        """
        if key not in self.store:
            return 0
        to_remove = [
            member
            for member, score in self.store[key].items()
            if min_score <= score <= max_score
        ]
        for member in to_remove:
            del self.store[key][member]

    def zcount(self, key, min_score, max_score):
        if key not in self.store:
            return 0
        return sum(1 for v in self.store[key].values() if min_score <= v <= max_score)


def make_transaction(tx_id: str, seconds_offset: int = 0):
    return Transaction(
        id=tx_id,
        amount=Decimal('10.00'),
        user_id='u1',
        location=Location(latitude=0.0, longitude=0.0),
        timestamp=datetime.now() + timedelta(seconds=seconds_offset)
    )


def test_rapid_transactions_below_limit():
    redis = DummyRedis()
    strat = RapidTransactionStrategy(redis_client=redis, max_transactions=3, window_minutes=5)

    # add three transactions within window
    for i in range(3):
        tx = make_transaction(f"t{i}", seconds_offset=i)
        res = strat.evaluate(tx)
        assert res['risk_level'] == RiskLevel.LOW_RISK


def test_rapid_transactions_exceed_limit():
    redis = DummyRedis()
    strat = RapidTransactionStrategy(redis_client=redis, max_transactions=2, window_minutes=5)

    # add three transactions within window -> exceed when >2
    for i in range(3):
        tx = make_transaction(f"t{i}", seconds_offset=i)
        res = strat.evaluate(tx)
    assert res['risk_level'] == RiskLevel.HIGH_RISK


def test_rapid_transactions_redis_error_handling(monkeypatch):
    class BadRedis:
        def zadd(self, *a, **k):
            raise Exception("redis down")

    strat = RapidTransactionStrategy(redis_client=BadRedis(), max_transactions=3, window_minutes=5)
    tx = make_transaction('t1')
    res = strat.evaluate(tx)
    assert res['risk_level'] == RiskLevel.LOW_RISK
    assert 'rapid_transaction_check_failed' in res['reasons']
