from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import router


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="FitBuddy",
    description="AI Fitness Plan Generator",
    version="1.0.0",
)


# ---------------------------------------------------------
# Static files
# ---------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

app.include_router(router)


# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------

@app.on_event("startup")
def startup_event():
    """
    Create the SQLite database and tables
    when the application starts.
    """
    init_db()


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "FitBuddy",
    }