"""
Extractors — Data extraction from PostgreSQL and external API sources.
"""
import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://analytics_user:analytics_pass_2026@database:5432/product_analytics"
)


def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def extract_sales_transactions(date_from=None, date_to=None):
    """Extract raw sales transactions from the database."""
    engine = get_engine()
    query = """
        SELECT
            s.id, s.transaction_id, s.product_id, s.region_id,
            s.quantity, s.unit_price, s.discount_pct, s.total_amount,
            s.transaction_date, s.channel, s.customer_segment,
            p.name AS product_name, p.sku, p.cost AS product_cost,
            p.category_id, c.name AS category_name,
            r.name AS region_name
        FROM sales_transactions s
        JOIN products p ON s.product_id = p.id
        JOIN categories c ON p.category_id = c.id
        JOIN regions r ON s.region_id = r.id
    """
    params = {}
    conditions = []

    if date_from:
        conditions.append("s.transaction_date >= :date_from")
        params["date_from"] = date_from
    if date_to:
        conditions.append("s.transaction_date <= :date_to")
        params["date_to"] = date_to

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY s.transaction_date"

    logger.info(f"Extracting sales transactions (from={date_from}, to={date_to})")
    df = pd.read_sql(text(query), engine, params=params)
    logger.info(f"Extracted {len(df)} sales records")
    return df


def extract_products():
    """Extract all product data."""
    engine = get_engine()
    query = """
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
    """
    df = pd.read_sql(text(query), engine)
    logger.info(f"Extracted {len(df)} products")
    return df


def extract_daily_metrics(date_from=None, date_to=None):
    """Extract existing daily metrics for comparison."""
    engine = get_engine()
    query = "SELECT * FROM daily_product_metrics"
    params = {}
    conditions = []

    if date_from:
        conditions.append("metric_date >= :date_from")
        params["date_from"] = date_from
    if date_to:
        conditions.append("metric_date <= :date_to")
        params["date_to"] = date_to

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    df = pd.read_sql(text(query), engine, params=params)
    logger.info(f"Extracted {len(df)} existing daily metrics")
    return df


def extract_from_api(endpoint, base_url=None):
    """Extract data from the internal REST API."""
    import requests
    base = base_url or os.getenv("API_BASE_URL", "http://api:8000")
    url = f"{base}{endpoint}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Extracted data from API: {endpoint}")

        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict) and "items" in data:
            return pd.DataFrame(data["items"])
        else:
            return pd.DataFrame([data])
    except Exception as e:
        logger.error(f"Failed to extract from API {endpoint}: {e}")
        return pd.DataFrame()
