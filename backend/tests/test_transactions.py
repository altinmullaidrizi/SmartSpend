from app.seed.generate import CATEGORY_RANGES, generate_transactions
from app.seed.merchants import CATEGORIES


def _auth_headers(client, email="u1@b.com", password="pw12345"):
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", json={"email": email, "password": password})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list(client):
    h = _auth_headers(client)
    r = client.post(
        "/transactions",
        json={"description": "Viva Fresh", "amount_eur": 12.5, "category": "groceries"},
        headers=h,
    )
    assert r.status_code == 201
    created = r.json()
    assert created["source"] == "manual"

    r = client.get("/transactions", headers=h)
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["description"] == "Viva Fresh"


def test_filter_by_category(client):
    h = _auth_headers(client)
    client.post(
        "/transactions",
        json={"description": "Viva Fresh", "amount_eur": 12.5, "category": "groceries"},
        headers=h,
    )
    client.post(
        "/transactions",
        json={"description": "Half & Half", "amount_eur": 2.0, "category": "coffee"},
        headers=h,
    )
    r = client.get("/transactions", params={"category": "coffee"}, headers=h)
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["category"] == "coffee"


def test_user_isolation(client):
    h1 = _auth_headers(client, email="one@b.com")
    h2 = _auth_headers(client, email="two@b.com")
    client.post(
        "/transactions",
        json={"description": "Secret", "amount_eur": 9.9},
        headers=h1,
    )
    r = client.get("/transactions", headers=h2)
    assert r.status_code == 200
    assert r.json() == []


def test_patch_and_delete(client):
    h = _auth_headers(client)
    r = client.post(
        "/transactions",
        json={"description": "Old", "amount_eur": 5.0},
        headers=h,
    )
    txn_id = r.json()["id"]

    r = client.patch(
        f"/transactions/{txn_id}", json={"description": "New"}, headers=h
    )
    assert r.status_code == 200
    assert r.json()["description"] == "New"

    r = client.delete(f"/transactions/{txn_id}", headers=h)
    assert r.status_code == 204

    r = client.get("/transactions", headers=h)
    assert all(t["id"] != txn_id for t in r.json())


def test_patch_other_user_404(client):
    h1 = _auth_headers(client, email="a1@b.com")
    h2 = _auth_headers(client, email="a2@b.com")
    r = client.post(
        "/transactions", json={"description": "Mine", "amount_eur": 1.0}, headers=h1
    )
    txn_id = r.json()["id"]
    r = client.patch(f"/transactions/{txn_id}", json={"description": "X"}, headers=h2)
    assert r.status_code == 404


def test_seed_endpoint(client):
    h = _auth_headers(client)
    r = client.post("/transactions/seed", params={"n": 30}, headers=h)
    assert r.status_code == 200
    assert r.json()["inserted"] == 30

    r = client.get("/transactions", headers=h)
    items = r.json()
    assert len(items) == 30
    for t in items:
        assert t["category"] in CATEGORIES
        assert t["source"] == "seed"


def test_generate_transactions_unit():
    txns = generate_transactions(50, user_id=1, seed=42)
    assert len(txns) == 50
    for t in txns:
        assert t.category in CATEGORIES
        low, high = CATEGORY_RANGES[t.category]
        assert low <= t.amount_eur <= high
        assert t.source == "seed"
        assert t.user_id == 1
