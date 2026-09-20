import csv
import os
import random
from datetime import datetime, timedelta
from typing import List, Optional

from app.models import Transaction
from app.seed.merchants import MERCHANTS

# Per-category EUR amount ranges tuned to Kosovo prices.
CATEGORY_RANGES = {
    "coffee": (1.0, 3.0),
    "dining": (3.0, 15.0),
    "groceries": (5.0, 60.0),
    "transport": (10.0, 50.0),
    "mobile_topup": (5.0, 20.0),
    "utilities": (20.0, 90.0),
    "rent": (150.0, 400.0),
    "shopping": (10.0, 120.0),
    "health": (5.0, 40.0),
    "education": (20.0, 200.0),
    "transfers": (20.0, 300.0),
    "entertainment": (5.0, 40.0),
}

# Optional short suffixes appended to a few descriptions for variety.
_SUFFIXES = ["", "", "", " - card", " - online", " - POS"]


def generate_transactions(
    n: int, user_id: int, seed: Optional[int] = None
) -> List[Transaction]:
    """Build n Transaction objects with Kosovo merchants and prices."""
    rng = random.Random(seed)
    merchant_names = list(MERCHANTS.keys())
    now = datetime.utcnow()

    transactions: List[Transaction] = []
    for _ in range(n):
        merchant = rng.choice(merchant_names)
        category = MERCHANTS[merchant]
        low, high = CATEGORY_RANGES[category]
        amount = round(rng.uniform(low, high), 2)
        description = merchant + rng.choice(_SUFFIXES)
        days_ago = rng.randint(0, 180)
        seconds = rng.randint(0, 86399)
        date = now - timedelta(days=days_ago, seconds=seconds)
        transactions.append(
            Transaction(
                user_id=user_id,
                date=date,
                description=description,
                amount_eur=amount,
                category=category,
                source="seed",
            )
        )
    return transactions


def export_training_csv(
    transactions: List[Transaction], path: str = "data/transactions.csv"
) -> str:
    """Write description,category rows to a CSV used for training."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["description", "category"])
        for txn in transactions:
            writer.writerow([txn.description, txn.category])
    return path
