from collections import namedtuple

from app.insights.budget import budget_tips, spend_by_category

Txn = namedtuple("Txn", ["category", "amount_eur"])


def _auth_headers(client, email="insights@b.com", password="pw12345"):
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", json={"email": email, "password": password})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_spend_by_category_totals_and_skips_none():
    txns = [
        Txn(category="groceries", amount_eur=10.0),
        Txn(category="groceries", amount_eur=5.5),
        Txn(category="coffee", amount_eur=2.0),
        Txn(category=None, amount_eur=100.0),
    ]
    result = spend_by_category(txns)
    assert result == {"groceries": 15.5, "coffee": 2.0}


def test_budget_tips_increase_warning_fires():
    previous = [Txn(category="dining", amount_eur=100.0)]
    current = [Txn(category="dining", amount_eur=140.0)]  # +40%
    tips = budget_tips(current, previous)
    warning_tips = [t for t in tips if t["severity"] == "warning"]
    assert len(warning_tips) == 1
    assert warning_tips[0]["category"] == "dining"
    assert "40" in warning_tips[0]["message"] or "%" in warning_tips[0]["message"]


def test_budget_tips_salary_threshold_fires():
    previous = []
    current = [Txn(category="rent", amount_eur=200.0)]  # > 0.3*550=165
    tips = budget_tips(current, previous)
    info_tips = [t for t in tips if t["severity"] == "info"]
    assert len(info_tips) == 1
    assert info_tips[0]["category"] == "rent"


def test_budget_tips_flat_low_spend_no_tips():
    previous = [Txn(category="coffee", amount_eur=20.0)]
    current = [Txn(category="coffee", amount_eur=21.0)]
    tips = budget_tips(current, previous)
    assert tips == []


def test_anomaly_flagged_via_api_and_visible_in_insights(client):
    h = _auth_headers(client)
    # Build up history of similar amounts in the same category.
    for amount in [10.0, 11.0, 10.5, 9.5, 11.5]:
        r = client.post(
            "/transactions",
            json={
                "description": "Viva Fresh",
                "amount_eur": amount,
                "category": "groceries",
            },
            headers=h,
        )
        assert r.status_code == 201
        assert r.json()["is_anomaly"] is False

    r = client.post(
        "/transactions",
        json={
            "description": "Viva Fresh",
            "amount_eur": 900.0,
            "category": "groceries",
        },
        headers=h,
    )
    assert r.status_code == 201
    outlier = r.json()
    assert outlier["is_anomaly"] is True

    r = client.get("/insights/anomalies", headers=h)
    assert r.status_code == 200
    anomalies = r.json()
    assert any(a["id"] == outlier["id"] for a in anomalies)

    r = client.get("/insights/summary", headers=h)
    assert r.status_code == 200
    summary = r.json()
    expected_groceries_total = round(10.0 + 11.0 + 10.5 + 9.5 + 11.5 + 900.0, 2)
    assert summary["by_category"]["groceries"] == expected_groceries_total
    assert summary["total"] == expected_groceries_total
