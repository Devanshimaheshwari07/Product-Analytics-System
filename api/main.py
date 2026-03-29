"""
Product Analytics — FastAPI Application
========================================
REST API for the End-to-End Product Analysis System.
Provides endpoints for products, sales, and analytics data.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import products, sales, analytics

app = FastAPI(
    title="Product Analytics API",
    description="Backend REST API for product performance monitoring and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
