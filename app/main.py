"""
main.py
-------
FastAPI application entry point.

Responsibilities:
  - Create FastAPI app instance
  - Register all routers
  - Run database table creation on startup (Base.metadata.create_all)
  - Mount static files directory for puzzle images
  - Provide a health-check root endpoint
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.routers import courses, lessons, quiz, ai_generation

# Import all models so SQLAlchemy registers them before create_all
import app.models.course    # noqa: F401
import app.models.lesson    # noqa: F401
import app.models.question  # noqa: F401
import app.models.option    # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Lifespan: runs on startup and shutdown ────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: create all database tables if they don't exist
    logger.info("Creating database tables (if not already created)...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready.")
    yield
    # SHUTDOWN: nothing to clean up for this demo


# ── FastAPI App Instance ──────────────────────────────────────────────────────

app = FastAPI(
    title="Cognitive Training Platform API",
    description=(
        "A demo backend for a cognitive training platform. "
        "Supports courses, lessons, quizzes, and AI-powered content generation "
        "using Groq LLM with Redis background workers."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── CORS Middleware ───────────────────────────────────────────────────────────
# Allow all origins for demo purposes — restrict in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Static Files ──────────────────────────────────────────────────────────────
# Puzzle images served from /static/puzzles/

app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(quiz.router)
app.include_router(ai_generation.router)


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Cognitive Training Platform API",
        "docs": "/docs",
        "version": "1.0.0",
    }
