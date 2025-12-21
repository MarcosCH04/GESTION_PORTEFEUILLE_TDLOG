# backend/tests/test_session.py
import pytest
from sqlalchemy.orm import Session
from app.db import User, UserStrategy, Session as SessionModel
from tests.test_api import USER_DATA, PAYLOAD_DATA, REGISTER_URL, LOGIN_URL

# --- Helper ---
def authenticated_client(client):
    client.post(REGISTER_URL, json=USER_DATA)
    login_response = client.post(LOGIN_URL, json=USER_DATA)
    
    # Debugging print: if this fails, we will see why
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        
    assert login_response.status_code == 200, "Helper failed to login"
    token = login_response.cookies.get("session_token")
    assert token is not None, "Session token cookie missing in login response"
    
    client.cookies.set("session_token", token)
    return client

# --- Tests ---

def test_strategy_scratchpad_persistence(client, db_session: Session):
    """
    Verifies that running multiple backtests only maintains ONE scratchpad 
    and that it survives logout.
    """
    auth_client = authenticated_client(client)
    
    # 1. Run backtest 3 times
    for _ in range(3):
        auth_client.post("/api/backtest", json=PAYLOAD_DATA)

    # 2. Verify: Only 1 scratchpad (is_saved=False) exists
    strategy_count = db_session.query(UserStrategy).count()
    assert strategy_count == 1 
    
    # 3. Logout
    auth_client.post("/api/logout")
    
    # 4. Verify Session is deleted, but Strategy remains
    session_exists = db_session.query(SessionModel).count() > 0
    assert session_exists is False
    assert db_session.query(UserStrategy).count() == 1

def test_scratchpad_overwrites_and_manual_save(client, db_session: Session):
    """
    Verifies the flow of running a backtest and then explicitly saving it.
    """
    auth_client = authenticated_client(client)
    
    # 1. Run backtest (Creates the scratchpad)
    auth_client.post("/api/backtest", json=PAYLOAD_DATA)
    
    # 2. Manually save it
    auth_client.post("/api/strategies/save-current")
    
    # 3. Verify: We now have 1 'Saved' and 1 'Latest' (scratchpad)
    # Total = 2 rows
    assert db_session.query(UserStrategy).filter_by(is_saved=True).count() == 1
    assert db_session.query(UserStrategy).filter_by(is_saved=False).count() == 1

def test_strategy_manual_save_limit(client, db_session: Session):
    """
    Verifies that a user can only have 5 saved strategies.
    """
    auth_client = authenticated_client(client)
    
    # 1. Run backtest (creates scratchpad)
    auth_client.post("/api/backtest", json=PAYLOAD_DATA)
    
    # 2. Save it 5 times
    for i in range(5):
        res = auth_client.post("/api/strategies/save-current")
        assert res.status_code == 200
        
    # 3. The 6th manual save should fail
    res = auth_client.post("/api/strategies/save-current")
    assert res.status_code == 400
    assert "Storage full" in res.json()["detail"]

    # 4. Final Count check
    # 1 (latest) + 5 (saved) = 6
    assert db_session.query(UserStrategy).count() == 6
    
    # 5. Logout and check session cleanup
    auth_client.post("/api/logout")
    assert db_session.query(SessionModel).count() == 0