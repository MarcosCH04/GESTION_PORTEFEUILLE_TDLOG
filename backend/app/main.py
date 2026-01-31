# backend/app/main.py

#This is the main entry point for the FastAPI backend application for the Investment Backtester project.
# It sets up the FastAPI app, configures CORS to allow requests from the frontend, Runs database initialization, and registers API routes.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .db import Base, engine # Import engine and Base
from .auth import create_db_and_tables # Import the initialization function


# 1. Initilize database tables on startup 
create_db_and_tables() 

# 2. Set up FastAPI appp 
app = FastAPI(title="Investment Backtester API")

# 3. Configuration for CORS to allow frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",        # Frontend Origin
        "http://127.0.0.1:5173",        # Frontend Origin IP
        "http://localhost:8000",        # Backend Self-Reference (needed for cookie/auth)
        "http://127.0.0.1:8000",        # Backend Self-Reference IP
    ], 
    allow_credentials=True,             # Critical for cookie transfer
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")