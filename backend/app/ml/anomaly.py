import statistics
from typing import List

Z_THRESHOLD = 3.0

# TODO: try IsolationForest here instead of the z-score, if there is time


def is_anomalous(amount: float, history_amounts: List[float]) -> bool:
    """Check if amount is an outlier compared to past amounts in the same category."""
    # Not enough history to say anything useful yet.
    if len(history_amounts) < 5:
        return False

    mean = statistics.mean(history_amounts)
    stdev = statistics.pstdev(history_amounts)

    if stdev < 1e-9:
        return abs(amount - mean) > 1e-9

    z = (amount - mean) / stdev
    return abs(z) > Z_THRESHOLD
