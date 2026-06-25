from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///smartspend.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create all tables defined on SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session
