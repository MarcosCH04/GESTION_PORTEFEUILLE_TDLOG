# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router

app = FastAPI(title="Investment Backtester API")

# CORS pour autoriser le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à resserrer en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
