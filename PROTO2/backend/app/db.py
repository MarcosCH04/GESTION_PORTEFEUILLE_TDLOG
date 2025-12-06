# backend/app/db.py

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, UniqueConstraint, Date
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func # <-- REQUIRED for server_default=func.now()
from datetime import datetime
import os

# --- 1. Database Setup ---
# Docker-persistent path for the SQLite file
DB_PATH = "/app/data/app.db" 
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}" 

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Required for SQLite with FastAPI/threads
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI Dependency: Provides a session and closes it automatically."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 2. Database Models ---

# Normalized 3NF Cache: One row = One Asset + One Day
class DailyPrice(Base):
    __tablename__ = "daily_price"

    id = Column(Integer, primary_key=True, index=True)
    ticker_symbol = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False) 
    price_data = Column(JSON, nullable=False) # Stores {"Close": price} etc.
    
    last_updated = Column(DateTime, server_default=func.now(), nullable=False)

    # Composite unique key ensures one record per ticker per day
    __table_args__ = (
        UniqueConstraint('ticker_symbol', 'date', name='uq_daily_price'),
    )

# User Identity Table (Authentication)
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) # Stores Argon2 hash
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    cases = relationship("UserCase", back_populates="user")

# User Session & Preference Storage
class UserCase(Base):
    __tablename__ = "user_case"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    session_token = Column(String, unique=True, index=True) 
    last_activity_time = Column(DateTime, default=datetime.utcnow, index=True) # 30-min timer (Python default is fine here)
    is_favorite = Column(Boolean, default=False)
    
    # JSON stores Pydantic models (CaseParameters/CaseResults)
    last_parameters = Column(JSON, nullable=False)
    calculated_results = Column(JSON) 
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="cases")