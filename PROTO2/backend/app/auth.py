import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from starlette.requests import Request
from passlib.context import CryptContext 

# Alias Session as SessionModel to distinguish from the Type Hint
from .db import User, UserStrategy, Session as SessionModel, Base, engine, get_db
from .schemas import UserCreate

# --- 1. Security Setup ---
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- 2. User CRUD (The "Missing" Functions) ---

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Retrieves a user by their unique username."""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Creates a new user record with a hashed password."""
    hashed = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- 3. Session Management ---

def create_user_session(db: Session, user: User) -> SessionModel:
    """Generates a token and stores it in the Session table."""
    session_token = secrets.token_urlsafe(32) 
    db_session = SessionModel(
        user_id=user.id,
        session_token=session_token,
        last_activity_time=datetime.utcnow(),
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """FastAPI Dependency: Authenticates the request via session cookie."""
    #Retrieve session token from cookies
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session token missing"
        )
    # Lock up token in database
    session_record = db.query(SessionModel).filter(SessionModel.session_token == token).first()

    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid session token"
        )

    # Check expiration (30 minutes of inactivity)
    if datetime.utcnow() - session_record.last_activity_time > timedelta(minutes=30):
        db.delete(session_record)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session expired"
        )

    # Sliding window: update activity on every request
    session_record.last_activity_time = datetime.utcnow()
    db.commit()
    
    # Return autenticated user    
    return session_record.user   

def create_db_and_tables():
    """Utility to initialize the SQLite schema."""
    Base.metadata.create_all(bind=engine)