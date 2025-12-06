# backend/app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, UniqueConstraint, Date
from datetime import datetime
import os

# --- Database Setup ---

# URL de la base SQLite.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = "/app/data/app.db" # Using the Docker-persistent path
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# create_engine pour SQLite (check_same_thread=False pour FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class from which all models will inherit
Base = declarative_base()


def get_db():
    """
    Dépendance FastAPI : fournit une session de base de données,
    et la ferme automatiquement après usage.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- SQLAlchemy Models ---

# Global API Cache Table
class DailyPrice(Base):
    __tablename__ = "daily_price"

    id = Column(Integer, primary_key=True, index=True)
    
    # Primary key components for granular caching
    ticker_symbol = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False) # Use Date type for date-only indexing

    # The actual price data (Close, High, Volume, etc.) for that day
    price_data = Column(JSON, nullable=False) 

    # Timestamp for future cache freshness checks
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Composite unique key ensures one price record per ticker per day
    __table_args__ = (
        UniqueConstraint('ticker_symbol', 'date', name='uq_daily_price'),
    )


# User Identity Table
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    # Store bcrypt-hashed passwords
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to user cases/sessions
    cases = relationship("UserCase", back_populates="user")


# User Session/Case Storage Table
class UserCase(Base):
    __tablename__ = "user_case"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key linking to the User
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    user = relationship("User", back_populates="cases")

    # Session Management fields
    session_token = Column(String, unique=True, index=True) 
    last_activity_time = Column(DateTime, default=datetime.utcnow, index=True) 

    # User Preferences/History fields
    is_favorite = Column(Boolean, default=False)
    case_name = Column(String) 
    
    # last_parameters (JSON) stores the Pydantic CaseParameters model
    last_parameters = Column(JSON, nullable=False)
    
    # calculated_results (JSON) stores the Pydantic CaseResults model
    calculated_results = Column(JSON) 
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)