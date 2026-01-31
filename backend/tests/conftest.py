# backend/tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 1. Import your FastAPI app and the Database components
from app.main import app
from app.db import Base, get_db

# --- DATABASE SETUP ---

# Use a shared in-memory SQLite database
# StaticPool is required for in-memory SQLite to persist data across multiple connections
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Creates the SQLAlchemy engine for the test session."""
    return create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

@pytest.fixture(scope="session")
def setup_test_db(engine):
    """Initializes the database schema once for the entire test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine, setup_test_db):
    """
    Provides a clean database session for every individual test.
    Wraps the test in a transaction that is rolled back at the end.
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to the connection
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = TestingSessionLocal()

    # --- CRITICAL: DEPENDENCY OVERRIDE ---
    # This forces the FastAPI app to use the test database session 
    # instead of the production one for all routes.
    app.dependency_overrides[get_db] = lambda: db

    yield db

    db.close()
    transaction.rollback()
    connection.close()
    
    # Clear the override after the test to keep the app 'clean'
    app.dependency_overrides.clear()


# --- TEST CLIENT SETUP ---

@pytest.fixture(scope="function")
def client(db_session):
    """
    Provides a FastAPI TestClient. 
    Because it's requested AFTER db_session, it uses the overridden database.
    """
    with TestClient(app) as c:
        yield c