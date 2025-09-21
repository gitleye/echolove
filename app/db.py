"""Database setup and session management.

This module configures the SQLAlchemy engine and session for the ECHOLOVE
project. By default, it connects to a local SQLite database, but the
connection string can be overridden with the `DATABASE_URL` environment
variable to point to a PostgreSQL database or another backend.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Read the database URL from environment or default to a local SQLite file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./echolove.db")

# SQLite requires a special flag to allow connections across threads
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create a SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
)

# Configure a session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


class Base(DeclarativeBase):
    """Base class for declarative models.

    All model classes in the project should inherit from this base class.
    """


def get_db():
    """Provide a transactional scope around a series of operations.

    Used as a dependency in FastAPI routes to get a session that is
    automatically closed after the request ends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()