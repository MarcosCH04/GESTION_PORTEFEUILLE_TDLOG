# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .db import Base, engine # Import engine and Base
from .auth import create_db_and_tables # Import the initialization function

# ----------------------------------------------------
# 1. INITIALIZE DATABASE TABLES ON STARTUP
# ----------------------------------------------------
create_db_and_tables() 


app = FastAPI(title="Investment Backtester API")

# CORS pour autoriser le frontend
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