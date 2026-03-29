"""
Transformers — Data cleaning, normalization, and feature engineering.
"""
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def clean_sales_data(df):
    """
    Clean raw sales data:
    - Remove duplicates
    - Handle null values
    - Validate data types
    - Remove outliers
    """
    if df.empty:
        logger.warning("Empty sales dataframe, skipping cleaning")
        return df

    initial_rows = len(df)

    # Remove exact duplicates
    df = df.drop_duplicates(subset=["transaction_id"], keep="first")

    # Handle null values
    df["discount_pct"] = df["discount_pct"].fillna(0)
    df["customer_segment"] = df["customer_segment"].fillna("unknown")
    df["channel"] = df["channel"].fillna("online")

    # Validate numeric fields — remove negative quantities and zero amounts
    df = df[df["quantity"] > 0]
    df = df[df["total_amount"] > 0]
    df = df[df["unit_price"] > 0]

    # Ensure discount is between 0 and 100
    df["discount_pct"] = df["discount_pct"].clip(0, 100)

    # Recalculate total_amount for consistency
    df["calculated_total"] = (
        df["unit_price"] * df["quantity"] * (1 - df["discount_pct"] / 100)
    ).round(2)

    # Flag significant discrepancies (> 1% difference)
    df["amount_discrepancy"] = abs(
        df["total_amount"] - df["calculated_total"]
    ) / df["total_amount"]
    discrepancy_count = (df["amount_discrepancy"] > 0.01).sum()
    if discrepancy_count > 0:
        logger.warning(f"Found {discrepancy_count} records with amount discrepancies")
        df.loc[df["amount_discrepancy"] > 0.01, "total_amount"] = df.loc[
            df["amount_discrepancy"] > 0.01, "calculated_total"
        ]

    df = df.drop(columns=["calculated_total", "amount_discrepancy"])

    removed = initial_rows - len(df)
    logger.info(f"Cleaned sales data: {initial_rows} → {len(df)} rows ({removed} removed)")

    return df


def normalize_categories(df):
    """Normalize category names to standard format."""
    if "category_name" in df.columns:
        df["category_name"] = df["category_name"].str.strip().str.title()
    return df


def normalize_channels(df):
    """Standardize channel names."""
    channel_map = {
        "online": "Online",
        "retail": "Retail",
        "wholesale": "Wholesale",
        "marketplace": "Marketplace",
    }
    if "channel" in df.columns:
        df["channel"] = df["channel"].str.lower().map(channel_map).fillna("Other")
    return df


def add_time_features(df):
    """Add time-based features for analysis."""
    if "transaction_date" not in df.columns:
        return df

    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["date"] = df["transaction_date"].dt.date
    df["year"] = df["transaction_date"].dt.year
    df["month"] = df["transaction_date"].dt.month
    df["week"] = df["transaction_date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["transaction_date"].dt.dayofweek
    df["hour"] = df["transaction_date"].dt.hour
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    return df


def compute_gross_profit(df):
    """Calculate gross profit per transaction."""
    if "product_cost" in df.columns and "total_amount" in df.columns:
        df["cost_of_goods"] = df["product_cost"] * df["quantity"]
        df["gross_profit"] = df["total_amount"] - df["cost_of_goods"]
        df["profit_margin"] = np.where(
            df["total_amount"] > 0,
            (df["gross_profit"] / df["total_amount"] * 100).round(2),
            0
        )
    return df


def aggregate_daily_metrics(df):
    """
    Aggregate cleaned transaction data into daily product-region metrics.
    """
    if df.empty:
        logger.warning("Empty dataframe, skipping aggregation")
        return pd.DataFrame()

    agg = df.groupby(["product_id", "region_id", "date"]).agg(
        total_revenue=("total_amount", "sum"),
        total_units_sold=("quantity", "sum"),
        total_orders=("id", "count"),
        avg_order_value=("total_amount", "mean"),
        avg_discount_pct=("discount_pct", "mean"),
        gross_profit=("gross_profit", "sum"),
    ).reset_index()

    agg["avg_order_value"] = agg["avg_order_value"].round(2)
    agg["avg_discount_pct"] = agg["avg_discount_pct"].round(2)
    agg["gross_profit"] = agg["gross_profit"].round(2)
    agg["total_revenue"] = agg["total_revenue"].round(2)

    # Calculate profit margin
    agg["profit_margin"] = np.where(
        agg["total_revenue"] > 0,
        (agg["gross_profit"] / agg["total_revenue"] * 100).round(2),
        0
    )

    agg = agg.rename(columns={"date": "metric_date"})

    logger.info(f"Aggregated into {len(agg)} daily metric records")
    return agg


def compute_kpi_summaries(daily_metrics_df):
    """
    Compute monthly KPI summaries from daily metrics.
    Returns a list of KPI dictionaries ready for database insertion.
    """
    if daily_metrics_df.empty:
        return []

    df = daily_metrics_df.copy()
    df["metric_date"] = pd.to_datetime(df["metric_date"])
    df["month_start"] = df["metric_date"].dt.to_period("M").dt.to_timestamp()

    kpis = []

    # Monthly overall KPIs
    monthly = df.groupby("month_start").agg(
        total_revenue=("total_revenue", "sum"),
        total_units=("total_units_sold", "sum"),
        total_orders=("total_orders", "sum"),
        gross_profit=("gross_profit", "sum"),
    ).reset_index()

    for _, row in monthly.iterrows():
        period_start = row["month_start"].date()
        period_end = (row["month_start"] + pd.offsets.MonthEnd(0)).date()

        for kpi_name, value, unit in [
            ("total_revenue", row["total_revenue"], "USD"),
            ("total_units_sold", row["total_units"], "units"),
            ("total_orders", row["total_orders"], "orders"),
            ("gross_profit", row["gross_profit"], "USD"),
        ]:
            kpis.append({
                "kpi_name": kpi_name,
                "kpi_value": round(float(value), 4),
                "kpi_unit": unit,
                "period_type": "monthly",
                "period_start": period_start,
                "period_end": period_end,
                "dimension_type": "overall",
                "dimension_value": "all",
            })

    # Compute AOV
    for _, row in monthly.iterrows():
        period_start = row["month_start"].date()
        period_end = (row["month_start"] + pd.offsets.MonthEnd(0)).date()
        aov = row["total_revenue"] / row["total_orders"] if row["total_orders"] > 0 else 0
        kpis.append({
            "kpi_name": "avg_order_value",
            "kpi_value": round(float(aov), 4),
            "kpi_unit": "USD",
            "period_type": "monthly",
            "period_start": period_start,
            "period_end": period_end,
            "dimension_type": "overall",
            "dimension_value": "all",
        })

    logger.info(f"Computed {len(kpis)} KPI summary records")
    return kpis


def transform_sales_pipeline(df):
    """
    Full transformation pipeline for sales data.
    """
    logger.info("Starting sales transformation pipeline")

    df = clean_sales_data(df)
    df = normalize_categories(df)
    df = normalize_channels(df)
    df = add_time_features(df)
    df = compute_gross_profit(df)

    logger.info("Sales transformation pipeline complete")
    return df
