# backend/app/auth.py

import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from starlette.requests import Request

# Third-party for secure hashing (Argon2)
from passlib.context import CryptContext 

from .db import SessionLocal, User, UserCase, Base, engine, get_db
from .schemas import UserCreate, CaseParameters, CaseResults

# --- 1. Utilities and Setup ---

# Argon2 is the industry standard hashing scheme
pwd_context = CryptContext(
    schemes=["argon2"], 
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """Hashes a password securely using Argon2."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_db_and_tables():
    """Initializes the database structure on startup."""
    Base.metadata.create_all(bind=engine)

SESSION_EXPIRATION_MINUTES = 1 


# --- 2. User CRUD and Session Management ---

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Retrieves a user by username."""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Creates a new user with a hashed password."""
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_session(db: Session, user: User, last_case: Optional[UserCase] = None) -> UserCase:
    """Creates a new session record upon successful login."""
    session_token = secrets.token_urlsafe(32) 
    
    # Retrieve stored data directly from the DB object (it's already serialized)
    params = last_case.last_parameters if last_case else "{}"
    results = last_case.calculated_results if last_case else None
    
    db_session = UserCase(
        user_id=user.id,
        session_token=session_token,
        last_activity_time=datetime.utcnow(),
        last_parameters=params, 
        calculated_results=results,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


# --- 3. FastAPI Dependency for Protected Routes ---

def get_current_active_user_case(
    request: Request, db: Session = Depends(get_db)
) -> UserCase:
    """Checks token, updates activity, and returns the UserCase for the active user."""
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token missing",
        )

    user_case = db.query(UserCase).filter(UserCase.session_token == token).first()

    if not user_case:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token")

    # Check for 30-minute inactivity expiration
    inactivity_limit = datetime.utcnow() - timedelta(minutes=SESSION_EXPIRATION_MINUTES)
    if user_case.last_activity_time < inactivity_limit:
        db.delete(user_case)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired due to inactivity. Please log in again.")

    # Update activity time for valid session
    user_case.last_activity_time = datetime.utcnow()
    db.commit()

    return user_case