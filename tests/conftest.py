from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.database import get_db
from app.main import app


# ------------------------------------------------------------
# Test database
# ------------------------------------------------------------
# SQLite in-memory database is fast and exists only during tests.
#
# StaticPool makes sure all connections use the same in-memory
# database. This is important when FastAPI runs code in another
# thread during TestClient requests.
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ------------------------------------------------------------
# Create tables once for the test database
# ------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def create_test_database() -> Generator[None, None, None]:
    """
    Create all database tables before the test session starts.

    The tables are removed after all tests finish.
    """
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


# ------------------------------------------------------------
# Database session for each test
# ------------------------------------------------------------

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Provide a fresh database session for each test.
    """

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------
# Override FastAPI's get_db dependency
# ------------------------------------------------------------

@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a TestClient that uses the test database
    instead of the real PostgreSQL database.
    """

    def override_get_db():
        yield db_session

    # Replace the production database dependency.
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Very important:
    # Remove the override after the test finishes so it
    # doesn't affect other tests.
    app.dependency_overrides.clear()