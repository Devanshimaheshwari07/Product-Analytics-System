"""
Pipeline — Main ETL orchestrator: extract → transform → load.
"""
import logging
from datetime import datetime, timedelta

from extractors import extract_sales_transactions
from transformers import transform_sales_pipeline, aggregate_daily_metrics, compute_kpi_summaries
from loaders import load_daily_metrics, load_kpi_summaries, update_change_percentages

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_incremental_pipeline():
    """
    Incremental ETL — processes only the last 2 days of data.
    Designed to run hourly to keep metrics up-to-date.
    """
    logger.info("=" * 60)
    logger.info("Starting INCREMENTAL ETL pipeline")
    logger.info("=" * 60)

    try:
        date_from = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # EXTRACT
        logger.info("Phase 1: EXTRACT")
        raw_sales = extract_sales_transactions(date_from=date_from, date_to=date_to)

        if raw_sales.empty:
            logger.info("No new sales data to process. Pipeline complete.")
            return

        # TRANSFORM
        logger.info("Phase 2: TRANSFORM")
        cleaned_sales = transform_sales_pipeline(raw_sales)
        daily_metrics = aggregate_daily_metrics(cleaned_sales)

        # LOAD
        logger.info("Phase 3: LOAD")
        metrics_loaded = load_daily_metrics(daily_metrics)

        # Compute and load KPIs
        kpis = compute_kpi_summaries(daily_metrics)
        kpis_loaded = load_kpi_summaries(kpis)

        # Update change percentages
        changes_updated = update_change_percentages()

        logger.info("=" * 60)
        logger.info(f"INCREMENTAL pipeline complete:")
        logger.info(f"  - Sales processed: {len(cleaned_sales)}")
        logger.info(f"  - Daily metrics loaded: {metrics_loaded}")
        logger.info(f"  - KPIs loaded: {kpis_loaded}")
        logger.info(f"  - Change %% updated: {changes_updated}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Incremental pipeline failed: {e}", exc_info=True)
        raise


def run_full_pipeline():
    """
    Full ETL — reprocesses ALL historical data.
    Designed to run once daily at midnight for complete refresh.
    """
    logger.info("=" * 60)
    logger.info("Starting FULL ETL pipeline")
    logger.info("=" * 60)

    try:
        # EXTRACT — all data
        logger.info("Phase 1: EXTRACT (full)")
        raw_sales = extract_sales_transactions()

        if raw_sales.empty:
            logger.info("No sales data found. Pipeline complete.")
            return

        # TRANSFORM
        logger.info("Phase 2: TRANSFORM")
        cleaned_sales = transform_sales_pipeline(raw_sales)
        daily_metrics = aggregate_daily_metrics(cleaned_sales)

        # LOAD
        logger.info("Phase 3: LOAD")
        metrics_loaded = load_daily_metrics(daily_metrics)

        # Compute and load KPIs
        kpis = compute_kpi_summaries(daily_metrics)
        kpis_loaded = load_kpi_summaries(kpis)

        # Update change percentages
        changes_updated = update_change_percentages()

        logger.info("=" * 60)
        logger.info(f"FULL pipeline complete:")
        logger.info(f"  - Total sales processed: {len(cleaned_sales)}")
        logger.info(f"  - Daily metrics loaded: {metrics_loaded}")
        logger.info(f"  - KPIs loaded: {kpis_loaded}")
        logger.info(f"  - Change %% updated: {changes_updated}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Full pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_full_pipeline()
