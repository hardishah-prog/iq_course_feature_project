"""
database.py
-----------
Sets up the SQLAlchemy database engine, session factory, and declarative base.

Usage:
    from app.database import SessionLocal, Base, engine
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load DATABASE_URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://iquser:iqpass@localhost:5432/iqdb")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session factory — each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


# Dependency for FastAPI routes — yields a DB session and closes it after use
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
