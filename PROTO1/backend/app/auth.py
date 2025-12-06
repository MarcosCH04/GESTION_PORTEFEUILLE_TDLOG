# backend/app/auth.py

from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from starlette.requests import Request

from .db import SessionLocal, User, UserCase
from .schemas import UserCreate, UserInDB, UserCaseBase
from .db import engine, Base # Ensure Base and engine are imported for table creation

# --- 1. Security Utilities ---
# Set up the context for hashing passwords
pwd_context = CryptContext(
    schemes=["argon2"], 
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """Hashes a password securely."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

# --- 2. Database Session Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. CRUD Operations ---

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- 4. Session/Login Logic ---

# Use secrets module for token generation
import secrets

SESSION_EXPIRATION_MINUTES = 30 # Your 30-minute inactivity requirement

def create_user_session(db: Session, user: User, last_case: Optional[UserCaseBase] = None) -> UserCase:
    """Creates a new session record for a user upon successful login."""
    # Generate a secure random token
    session_token = secrets.token_urlsafe(32) 
    
    # Use default/empty values if no case is provided
    params = last_case.last_parameters if last_case else "{}"
    results = last_case.calculated_results if last_case else None
    
    db_session = UserCase(
        user_id=user.id,
        session_token=session_token,
        last_activity_time=datetime.utcnow(),
        is_favorite=False,
        last_parameters=params,
        calculated_results=results,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_current_active_user_case(
    request: Request, db: Session = Depends(get_db)
) -> UserCase:
    """
    FastAPI Dependency to check for a valid, unexpired session token in cookies.
    If valid, updates activity time and returns the UserCase object.
    """
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token missing",
        )

    # 1. Find the session case
    user_case = db.query(UserCase).filter(UserCase.session_token == token).first()

    if not user_case:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token",
        )

    # 2. Check for expiration (30 minutes of inactivity)
    now = datetime.utcnow()
    inactivity_limit = now - timedelta(minutes=SESSION_EXPIRATION_MINUTES)

    if user_case.last_activity_time < inactivity_limit:
        # Session has expired due to inactivity
        db.delete(user_case)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired due to inactivity. Please log in again.",
        )

    # 3. Session is valid: Update activity time and commit
    user_case.last_activity_time = now
    db.commit()

    return user_case

# --- 5. Database Setup (to be called once) ---

def create_db_and_tables():
    """Create all tables defined in Base (User, AssetCache, UserCase)."""
    Base.metadata.create_all(bind=engine)

# Note: You should call create_db_and_tables() when your application starts up.