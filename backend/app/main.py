from fastapi import FastAPI
from app.db import init_db
from app import models  # noqa: F401  (register tables on SQLModel metadata)
from app.routers.auth import router as auth_router

app = FastAPI(title="SmartSpend")

app.include_router(auth_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "currency": "EUR"}
