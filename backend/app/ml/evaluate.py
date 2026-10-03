"""Extra evaluation of the categorizer and the anomaly detector.

Run from the backend/ directory:

    python -m app.ml.evaluate
"""

import random

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from app.ml.anomaly import is_anomalous
from app.ml.train import build_pipeline
from app.seed.generate import CATEGORY_RANGES, generate_transactions
from app.seed.merchants import MERCHANTS

SEED = 42
HISTORY_LEN = 10
HISTORIES_PER_CATEGORY = 20
OUTLIER_FACTORS = [3, 5, 10]


def _pos_prefix(text: str, rng: random.Random) -> str:
    return f"POS {rng.randint(1000, 9999)} {text}"


def _cut_off(text: str) -> str:
    return text.upper().replace(" ", "")[:8]


def _noise_types(rng: random.Random):
    return {
        "clean": lambda t: t,
        "uppercase": lambda t: t.upper(),
        "no spaces": lambda t: t.replace(" ", ""),
        "POS prefix": lambda t: _pos_prefix(t, rng),
        "cut-off name": _cut_off,
        "city suffix": lambda t: t + " PRISHTINE",
    }


def _dataset():
    txns = generate_transactions(n=3000, user_id=0, seed=SEED)
    return [t.description for t in txns], [t.category for t in txns]


def _print_table(title, header, rows):
    print(f"\n{title}")
    widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
    line = "  ".join(str(h).ljust(w) for h, w in zip(header, widths))
    print(line)
    print("-" * len(line))
    for row in rows:
        print("  ".join(str(c).ljust(w) for c, w in zip(row, widths)))


def eval_noise():
    X, y = _dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED
    )
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    rng = random.Random(SEED)
    rows = []
    for name, noise in _noise_types(rng).items():
        noisy = [noise(t) for t in X_test]
        acc = accuracy_score(y_test, pipeline.predict(noisy))
        rows.append([name, f"{acc:.3f}"])
    _print_table("Categorizer robustness (noisy descriptions)", ["noise", "accuracy"], rows)


def _held_out_merchants():
    """Last merchant of each category that has more than one merchant."""
    by_category = {}
    for merchant, category in MERCHANTS.items():
        by_category.setdefault(category, []).append(merchant)
    return {ms[-1]: c for c, ms in by_category.items() if len(ms) > 1}


def _merchant_of(description: str) -> str:
    return next(m for m in MERCHANTS if description.startswith(m))


def eval_unseen_merchants():
    X, y = _dataset()
    held_out = _held_out_merchants()
    train = [(x, c) for x, c in zip(X, y) if _merchant_of(x) not in held_out]
    test = [(x, c) for x, c in zip(X, y) if _merchant_of(x) in held_out]

    pipeline = build_pipeline()
    pipeline.fit([x for x, _ in train], [c for _, c in train])
    y_pred = pipeline.predict([x for x, _ in test])

    rows = []
    for merchant, category in held_out.items():
        pairs = [(c, p) for (x, c), p in zip(test, y_pred) if _merchant_of(x) == merchant]
        acc = sum(c == p for c, p in pairs) / len(pairs)
        rows.append([merchant, category, len(pairs), f"{acc:.3f}"])
    total = accuracy_score([c for _, c in test], y_pred)
    rows.append(["ALL", "", len(test), f"{total:.3f}"])
    _print_table(
        "Unseen merchants (one per category held out; rent has only one merchant)",
        ["merchant", "category", "n", "accuracy"],
        rows,
    )


def eval_anomaly():
    rng = random.Random(SEED)
    header = ["category"] + [f"detect {f}x" for f in OUTLIER_FACTORS] + ["false pos"]
    rows = []
    totals = {f: 0 for f in OUTLIER_FACTORS}
    total_fp = 0
    for category, (low, high) in CATEGORY_RANGES.items():
        hits = {f: 0 for f in OUTLIER_FACTORS}
        fp = 0
        for _ in range(HISTORIES_PER_CATEGORY):
            history = [round(rng.uniform(low, high), 2) for _ in range(HISTORY_LEN)]
            for f in OUTLIER_FACTORS:
                hits[f] += is_anomalous(high * f, history)
            fp += is_anomalous(round(rng.uniform(low, high), 2), history)
        for f in OUTLIER_FACTORS:
            totals[f] += hits[f]
        total_fp += fp
        n = HISTORIES_PER_CATEGORY
        rows.append([category] + [f"{hits[f] / n:.2f}" for f in OUTLIER_FACTORS] + [f"{fp / n:.2f}"])
    n = HISTORIES_PER_CATEGORY * len(CATEGORY_RANGES)
    rows.append(["ALL"] + [f"{totals[f] / n:.2f}" for f in OUTLIER_FACTORS] + [f"{total_fp / n:.2f}"])
    _print_table(
        f"Anomaly detector ({HISTORIES_PER_CATEGORY} histories of {HISTORY_LEN} per category)",
        header,
        rows,
    )


def main():
    eval_noise()
    eval_unseen_merchants()
    eval_anomaly()


if __name__ == "__main__":
    main()
