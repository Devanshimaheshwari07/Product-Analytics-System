"""
Database connection and session management.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Build DATABASE_URL from individual env vars so it always matches the
# credentials injected by docker-compose (POSTGRES_PASSWORD, POSTGRES_HOST, etc.)
# rather than relying on a hardcoded fallback with a different password/host.
DATABASE_URL = os.getenv("DATABASE_URL") or (
    "postgresql://{user}:{password}@{host}:{port}/{db}".format(
        user=os.getenv("POSTGRES_USER", "analytics_user"),
        password=os.getenv("POSTGRES_PASSWORD", "secure_password_change_me"),
        host=os.getenv("POSTGRES_HOST", "database"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        db=os.getenv("POSTGRES_DB", "product_analytics"),
    )
)

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
