"""
Product Analytics — FastAPI Application
========================================
REST API for the End-to-End Product Analysis System.
Provides endpoints for products, sales, and analytics data.
"""
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database import engine
from routers import products, sales, analytics

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: wait for database to be available before accepting requests."""
    max_retries = 15
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection established")
            break
        except Exception as e:
            logger.warning(f"⏳ Waiting for database (attempt {attempt}/{max_retries}): {e}")
            if attempt == max_retries:
                logger.error("❌ Could not connect to database after max retries")
                raise
            time.sleep(3)
    yield


app = FastAPI(
    title="Product Analytics API",
    description="Backend REST API for product performance monitoring and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS Middleware ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routers ────────────────────────────────────────
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(analytics.router)


# ─── Health Check ─────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "product-analytics-api", "version": "1.0.0"}


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Product Analytics API",
        "docs": "/docs",
        "health": "/health",
    }
