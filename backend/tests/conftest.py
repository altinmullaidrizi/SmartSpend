import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

import app.models  # noqa: F401  (register tables on SQLModel.metadata)
from app.main import app as fastapi_app
from app.db import get_session


@pytest.fixture
def client():
    """TestClient backed by an isolated in-memory SQLite database."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = override_get_session
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)
