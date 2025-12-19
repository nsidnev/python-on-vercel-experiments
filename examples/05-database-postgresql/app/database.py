"""
Database configuration with NullPool for serverless

CRITICAL: Serverless functions are stateless and ephemeral.
Python lacks proper connection lifecycle hooks (unlike Node.js's attachDatabasePool),
so we use NullPool to avoid connection leaking during function suspension.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# CRITICAL: Use NullPool for serverless (no connection pooling)
#
# Why NullPool?
# - Python doesn't have waitUntil/attachDatabasePool like Node.js
# - Traditional pooling (QueuePool) can leak connections during function suspension
# - pool_recycle only checks age on checkout, not during suspension
# - NullPool creates a new connection per checkout and closes it on return
#
# Trade-offs:
# ✅ No connection leaks during function suspension
# ✅ Simple and predictable behavior
# ✅ Works reliably in serverless environments
# ⚠️  Slightly higher latency (new connection per request)
# ⚠️  No connection reuse within a function instance
#
# For high-traffic applications, consider using Neon's connection pooler (PgBouncer)
# which handles pooling at the database level: https://neon.tech/docs/connect/connection-pooling

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # No connection pooling - create/close per request
    echo=False,  # Set to True for SQL query logging (debugging)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


@contextmanager
def get_db():
    """
    Context manager for database sessions

    Usage:
        with get_db() as db:
            result = db.query(Model).all()

    The session is automatically closed after the context exits.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_dependency():
    """
    FastAPI dependency for database sessions

    Usage:
        @app.get("/items")
        def list_items(db: Session = Depends(get_db_dependency)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables

    Creates all tables defined in models.
    Call this once to set up the database schema.
    """
    from app import models  # Import here to avoid circular dependency

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def test_connection():
    """
    Test database connection

    Returns True if connection is successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
