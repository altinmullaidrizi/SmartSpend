from __future__ import annotations

import statistics
from typing import List

MIN_HISTORY = 5
Z_THRESHOLD = 3.0
EPSILON = 1e-9


def is_anomalous(amount: float, history_amounts: List[float]) -> bool:
    """Decide whether `amount` is an outlier vs. past amounts in the same category.

    Pure function -- no DB access -- so it can be unit tested directly.
    """
    if len(history_amounts) < MIN_HISTORY:
        return False

    mean = statistics.mean(history_amounts)
    stdev = statistics.pstdev(history_amounts)

    if stdev < EPSILON:
        return abs(amount - mean) > EPSILON

    z = (amount - mean) / stdev
    return abs(z) > Z_THRESHOLD
