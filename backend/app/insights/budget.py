from __future__ import annotations

from typing import Dict, List

AVG_NET_SALARY_EUR = 550


def spend_by_category(transactions: List) -> Dict[str, float]:
    """Aggregate total amount_eur per category. Transactions with no
    category are ignored. Pure function -- no DB access."""
    totals: Dict[str, float] = {}
    for txn in transactions:
        category = txn.category
        if category is None:
            continue
        totals[category] = totals.get(category, 0.0) + txn.amount_eur
    return {cat: round(total, 2) for cat, total in totals.items()}


def budget_tips(current_month_txns: List, previous_month_txns: List) -> List[dict]:
    """Compare per-category spend for the current period vs. the previous
    period and produce Kosovo-contextualized budget tips. Pure function --
    no DB access."""
    current_totals = spend_by_category(current_month_txns)
    previous_totals = spend_by_category(previous_month_txns)

    categories = set(current_totals) | set(previous_totals)
    tips: List[dict] = []

    for cat in categories:
        current = current_totals.get(cat, 0.0)
        previous = previous_totals.get(cat, 0.0)

        if previous > 0 and current > previous * 1.25:
            pct = round(((current - previous) / previous) * 100)
            tips.append(
                {
                    "category": cat,
                    "message": (
                        f"Your {cat} spending is up {pct}% "
                        "compared to last month."
                    ),
                    "severity": "warning",
                }
            )

        if current > 0.3 * AVG_NET_SALARY_EUR:
            tips.append(
                {
                    "category": cat,
                    "message": (
                        "You've spent over 30% of an average Kosovo salary "
                        f"on {cat} this month."
                    ),
                    "severity": "info",
                }
            )

    return tips
