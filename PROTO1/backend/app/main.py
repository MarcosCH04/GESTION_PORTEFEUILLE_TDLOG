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
    # Ensure this matches your frontend Docker port (5173)
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173",
                   "http://localhost:8000", "http://127.0.0.1:8000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")