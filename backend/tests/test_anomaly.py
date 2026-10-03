from app.ml.anomaly import is_anomalous


def test_not_enough_history_returns_false():
    assert is_anomalous(500.0, [10.0, 11.0, 12.0]) is False


def test_wild_outlier_flagged_true():
    history = [10.0, 11.0, 12.0, 10.5, 11.5]
    assert is_anomalous(500.0, history) is True


def test_consistent_amount_not_flagged():
    history = [10.0, 11.0, 12.0, 10.5, 11.5]
    assert is_anomalous(11.0, history) is False


def test_constant_history_small_change_not_flagged():
    history = [300.0] * 5
    assert is_anomalous(305.0, history) is False
    assert is_anomalous(3000.0, history) is True
