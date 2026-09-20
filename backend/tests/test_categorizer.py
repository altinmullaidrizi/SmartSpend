import pytest

from app.ml import categorizer
from app.ml.train import build_pipeline
from app.seed.generate import generate_transactions
from app.seed.merchants import CATEGORIES


def _train_small_pipeline(n: int = 500, seed: int = 1):
    """Train a small in-memory pipeline for deterministic, file-free tests."""
    txns = generate_transactions(n, user_id=0, seed=seed)
    X = [t.description for t in txns]
    y = [t.category for t in txns]
    pipeline = build_pipeline()
    pipeline.fit(X, y)
    return pipeline


@pytest.fixture
def injected_model():
    """Inject a small trained pipeline into the categorizer module."""
    original = categorizer._model
    categorizer._model = _train_small_pipeline()
    yield categorizer._model
    categorizer._model = original


def test_predict_returns_none_when_not_loaded():
    original = categorizer._model
    categorizer._model = None
    try:
        assert categorizer.predict_category("Viva Fresh") is None
    finally:
        categorizer._model = original


def test_predict_category_valid(injected_model):
    assert categorizer.is_loaded() is True
    pred = categorizer.predict_category("Viva Fresh")
    assert pred in CATEGORIES
    # A well-known grocery merchant should map to groceries.
    assert pred == "groceries"


def test_predict_various_merchants(injected_model):
    for description in ["Half & Half", "KEDS", "Vala", "Kinema ABC"]:
        assert categorizer.predict_category(description) in CATEGORIES


def test_api_autocategorizes(client, injected_model):
    client.post("/auth/register", json={"email": "cat@b.com", "password": "pw12345"})
    r = client.post("/auth/login", json={"email": "cat@b.com", "password": "pw12345"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # POST without a category -> the backend should auto-fill it.
    r = client.post(
        "/transactions",
        json={"description": "Viva Fresh", "amount_eur": 12.5},
        headers=headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["category"] is not None
    assert body["category"] in CATEGORIES
