from fastapi import FastAPI
from app.db import init_db
from app import models  # noqa: F401  (register tables on SQLModel metadata)
from app.ml import categorizer
from app.routers.auth import router as auth_router
from app.routers.transactions import router as txn_router
from app.routers.insights import router as insights_router

app = FastAPI(title="SmartSpend")

app.include_router(auth_router)
app.include_router(txn_router)
app.include_router(insights_router)


@app.on_event("startup")
def on_startup():
    init_db()
    # Load the trained categorizer if present. A missing model file must not
    # crash the app -- auto-categorization is simply disabled until trained.
    if not categorizer.load_model():
        print(
            "WARNING: categorizer model not found; "
            "transactions will not be auto-categorized. "
            "Run `python -m app.ml.train` to create it."
        )


@app.get("/health")
def health():
    return {"status": "ok", "currency": "EUR"}
