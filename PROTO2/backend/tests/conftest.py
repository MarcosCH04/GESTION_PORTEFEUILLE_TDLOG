# backend/tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import core components from your application
from app.main import app
from app.db import Base, get_db

# --- 1. Test Database Setup ---

# Use an in-memory SQLite DB for maximum speed and isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:" 

@pytest.fixture(scope="session")
def engine():
    """Provides a SQLAlchemy engine connected to the in-memory test database."""
    return create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

@pytest.fixture(scope="session")
def setup_test_db(engine):
    """Creates all database tables defined in Base.metadata."""
    # This runs once per test session
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup is often omitted for in-memory DBs, but kept for robustness
    Base.metadata.drop_all(bind=engine) 

@pytest.fixture(scope="function")
def db_session(engine, setup_test_db):
    """
    Provides a transactional database session for each test function.
    All changes are rolled back after the test completes.
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create a new session bound to the connection
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = TestingSessionLocal()
    
    # CRITICAL: Override FastAPI's dependency to use the test session
    app.dependency_overrides[get_db] = lambda: db

    yield db

    # 1. Rollback transaction to clean the database state
    db.close()
    transaction.rollback()
    connection.close()
    
    # 2. Clean up the dependency override
    app.dependency_overrides = {}


# --- 2. Test Client Fixture ---
@pytest.fixture(scope="function")
def client(db_session):
    """Provides an instance of FastAPI's TestClient for making API calls."""
    # The client uses the dependency override set in db_session
    return TestClient(app)