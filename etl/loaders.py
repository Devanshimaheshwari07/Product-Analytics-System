"""
Loaders — Write transformed data back to the database.
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


def load_daily_metrics(metrics_df):
    """
    Upsert daily product metrics into the database.
    Uses INSERT ... ON CONFLICT for idempotent writes.
    """
    if metrics_df.empty:
        logger.warning("No daily metrics to load")
        return 0

    engine = get_engine()
    loaded = 0

    upsert_sql = text("""
        INSERT INTO daily_product_metrics
            (product_id, region_id, metric_date, total_revenue, total_units_sold,
             total_orders, avg_order_value, avg_discount_pct, gross_profit, profit_margin)
        VALUES
            (:product_id, :region_id, :metric_date, :total_revenue, :total_units_sold,
             :total_orders, :avg_order_value, :avg_discount_pct, :gross_profit, :profit_margin)
        ON CONFLICT (product_id, region_id, metric_date) DO UPDATE SET
            total_revenue    = EXCLUDED.total_revenue,
            total_units_sold = EXCLUDED.total_units_sold,
            total_orders     = EXCLUDED.total_orders,
            avg_order_value  = EXCLUDED.avg_order_value,
            avg_discount_pct = EXCLUDED.avg_discount_pct,
            gross_profit     = EXCLUDED.gross_profit,
            profit_margin    = EXCLUDED.profit_margin
    """)

    with engine.begin() as conn:
        for _, row in metrics_df.iterrows():
            conn.execute(upsert_sql, {
                "product_id": int(row["product_id"]),
                "region_id": int(row["region_id"]),
                "metric_date": row["metric_date"],
                "total_revenue": float(row["total_revenue"]),
                "total_units_sold": int(row["total_units_sold"]),
                "total_orders": int(row["total_orders"]),
                "avg_order_value": float(row["avg_order_value"]),
                "avg_discount_pct": float(row["avg_discount_pct"]),
                "gross_profit": float(row["gross_profit"]),
                "profit_margin": float(row["profit_margin"]),
            })
            loaded += 1

    logger.info(f"Loaded {loaded} daily metric records")
    return loaded


def load_kpi_summaries(kpis):
    """
    Upsert KPI summary records into the database.
    """
    if not kpis:
        logger.warning("No KPI summaries to load")
        return 0

    engine = get_engine()
    loaded = 0

    upsert_sql = text("""
        INSERT INTO kpi_summary
            (kpi_name, kpi_value, kpi_unit, period_type, period_start, period_end,
             dimension_type, dimension_value)
        VALUES
            (:kpi_name, :kpi_value, :kpi_unit, :period_type, :period_start, :period_end,
             :dimension_type, :dimension_value)
        ON CONFLICT (kpi_name, period_type, period_start, dimension_type, dimension_value)
        DO UPDATE SET
            kpi_value = EXCLUDED.kpi_value
    """)

    with engine.begin() as conn:
        for kpi in kpis:
            conn.execute(upsert_sql, kpi)
            loaded += 1

    logger.info(f"Loaded {loaded} KPI summary records")
    return loaded


def update_change_percentages():
    """
    Calculate month-over-month change percentages for KPIs.
    """
    engine = get_engine()

    update_sql = text("""
        UPDATE kpi_summary AS curr
        SET
            previous_value = prev.kpi_value,
            change_pct = CASE
                WHEN prev.kpi_value IS NOT NULL AND prev.kpi_value != 0
                THEN ROUND(((curr.kpi_value - prev.kpi_value) / prev.kpi_value * 100)::numeric, 2)
                ELSE NULL
            END
        FROM kpi_summary AS prev
        WHERE curr.kpi_name = prev.kpi_name
          AND curr.period_type = prev.period_type
          AND curr.dimension_type = prev.dimension_type
          AND curr.dimension_value = prev.dimension_value
          AND curr.period_start = (prev.period_start + INTERVAL '1 month')::date
    """)

    with engine.begin() as conn:
        result = conn.execute(update_sql)
        logger.info(f"Updated change percentages for {result.rowcount} KPI records")

    return result.rowcount
