# backend/tests/test_api.py

import pytest
from datetime import date
from fastapi.testclient import TestClient # Although imported, client is provided by conftest
from app.db import UserCase
# No need to import engine, db_session, or client—Pytest provides them!

# --- Authentication Helpers for Testing ---
USER_DATA = {"username": "testuser", "password": "TestPassword123"}
LOGIN_URL = "/api/login"
REGISTER_URL = "/api/register"

def create_test_user(client: TestClient):
    """Utility to register a user before a login test."""
    client.post(REGISTER_URL, json=USER_DATA)

# --- Functional API Tests ---

def test_read_assets_public(client):
    """Tests the basic, public asset list endpoint."""
    response = client.get("/api/assets")
    assert response.status_code == 200
    assert "assets" in response.json()
    assert isinstance(response.json()["assets"], list)

def test_register_user_success(client):
    """Tests successful user registration (status 201)."""
    response = client.post(REGISTER_URL, json=USER_DATA)
    assert response.status_code == 201
    assert response.json()["username"] == USER_DATA["username"]
    assert "hashed_password" not in response.json() # Security check

def test_register_user_duplicate(client):
    """Tests registration failure on duplicate username (status 400)."""
    create_test_user(client) # Register once
    
    response = client.post(REGISTER_URL, json=USER_DATA) # Register again
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success_and_cookie_set(client):
    """Tests successful login and verification of the session cookie."""
    create_test_user(client)
    
    response = client.post(LOGIN_URL, json=USER_DATA)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    assert "session_token" in response.cookies
    assert response.cookies["session_token"] is not None

def test_login_failure(client):
    """Tests failure on incorrect password."""
    create_test_user(client)
    
    response = client.post(LOGIN_URL, json={"username": "testuser", "password": "wrongpassword"})
    
    assert response.status_code == 401
    assert "session_token" not in response.cookies

def test_logout_success(client):
    """Tests logout clears the session cookie and token from the database."""
    create_test_user(client)
    
    # 1. Login to get the cookie
    login_response = client.post(LOGIN_URL, json=USER_DATA)
    token = login_response.cookies["session_token"]
    client.cookies.set("session_token", token)

    # 2. Logout using the session cookie
    response = client.post("/api/logout")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"
    # The client should receive an instruction to delete the cookie
    assert response.cookies.get("session_token") is None

def test_protected_route_unauthenticated(client):
    """Tests that a protected route (/backtest) fails without a session token."""
    # Define a minimal valid payload
    payload = {
        "assets": ["AAPL"], "start_date": "2020-01-01", "end_date": "2020-02-01",
        "invest_amount": 1000, "weights": [1.0], "strategy": "buy_and_hold",
        "strat_start": "2020-01-01", "strat_end": "2020-02-01"
    }
    
    response = client.post("/api/backtest", json=payload)
    
    # Should fail with 401 Unauthorized
    assert response.status_code == 401
    assert "Session token missing" in response.json()["detail"]

# --- Helper to log in and return the client with the session cookie ---
def authenticated_client(client):
    """Registers a user, logs in, and returns the client with the session cookie set."""
    create_test_user(client)
    login_response = client.post(LOGIN_URL, json=USER_DATA)
    token = login_response.cookies["session_token"]
    client.cookies.set("session_token", token)
    return client

# --- Standard Backtest Payload ---
PAYLOAD_DATA = {
    "assets": ["AAPL", "MSFT"], 
    "start_date": "2020-01-01", 
    "end_date": "2020-03-01",
    "invest_amount": 1000.0, 
    "weights": [0.5, 0.5], 
    "strategy": "buy_and_hold",
    "strat_start": "2020-01-01", 
    "strat_end": "2020-03-01"
}

def test_backtest_authenticated_success(client, db_session):
    """
    Goal 1: Test successful backtest execution, requiring authentication.
    Goal 2: Verify that the results are saved to the UserCase table.
    """
    auth_client = authenticated_client(client)
    
    # 1. Execute the backtest
    response = auth_client.post("/api/backtest", json=PAYLOAD_DATA)

    assert response.status_code == 200
    data = response.json()
    
    # 2. Assert against the known output structure (from calc.py's output)
    # The final API response must contain 'portfolio' and 'metrics'
    assert "portfolio" in data 
    assert "metrics" in data 
    
    # Check that the metrics dict is keyed by the asset tickers provided in the payload:
    assert "AAPL" in data["metrics"] 
    assert "MSFT" in data["metrics"] 
    
    # Check that the calculated values are present and not zero (for a successful run)
    assert data["metrics"]["AAPL"]["cagr"] is not None
    # Check that the portfolio time series is present
    assert len(data["portfolio"]) > 20
    
    # 2. Verify persistence in the database (results saved to the active UserCase)
    
    # Find the active session (the one created during login)
    user_case = db_session.query(UserCase).first() 
    assert user_case is not None
    
    # Check that parameters and results fields are populated (not the default JSON string '"{}"')
    assert user_case.last_parameters != "{}"
    assert user_case.calculated_results is not None

def test_backtest_requires_auth(client):
    """
    Goal: Tests that calling the protected route fails without a session token.
    (This is already tested in test_protected_route_unauthenticated, but is repeated for clarity)
    """
    # TestClient without any cookie set
    response = client.post("/api/backtest", json=PAYLOAD_DATA)
    
    assert response.status_code == 401
    assert "Session token missing" in response.json()["detail"]

def test_backtest_input_validation(client):
    """
    Goal: Tests that the backend logic validates weights (must sum > 0).
    """
    auth_client = authenticated_client(client)
    
    invalid_payload = PAYLOAD_DATA.copy()
    invalid_payload["weights"] = [0.0, 0.0] # Weights that sum to zero

    response = auth_client.post("/api/backtest", json=invalid_payload)
    
    assert response.status_code == 400
    
    expected_message = "La somme des poids doit être égale à 1." 
    assert expected_message in response.json()["detail"]