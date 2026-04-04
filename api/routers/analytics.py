"""
Analytics router — KPI endpoints, performance rankings, and trend data.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text, case
from typing import Optional
from datetime import date

from database import get_db
from models import (
    DailyProductMetric, KPISummary, Product, Category, Region, SalesTransaction
)
from schemas import (
    KPIResponse, ProductPerformance, RegionalPerformance,
    CategoryPerformance, RevenueTrend, OverviewKPIs,
    ChannelDistribution, DiscountImpact
)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewKPIs)
def get_overview(db: Session = Depends(get_db)):
    """Get high-level overview KPIs."""
    metrics = db.query(
        func.coalesce(func.sum(DailyProductMetric.total_revenue), 0).label("revenue"),
        func.coalesce(func.sum(DailyProductMetric.total_orders), 0).label("orders"),
        func.coalesce(func.sum(DailyProductMetric.total_units_sold), 0).label("units"),
        func.coalesce(func.round(func.avg(DailyProductMetric.avg_order_value), 2), 0).label("aov"),
        func.coalesce(func.sum(DailyProductMetric.gross_profit), 0).label("profit"),
        func.coalesce(func.round(func.avg(DailyProductMetric.profit_margin), 2), 0).label("margin"),
    ).first()

    total_products = db.query(func.count(Product.id)).scalar()
    active_regions = db.query(func.count(Region.id)).scalar()

    return OverviewKPIs(
        total_revenue=metrics.revenue,
        total_orders=metrics.orders,
        total_units_sold=metrics.units,
        avg_order_value=metrics.aov,
        gross_profit=metrics.profit,
        avg_profit_margin=metrics.margin,
        total_products=total_products,
        active_regions=active_regions,
    )


@router.get("/revenue-trends", response_model=list[RevenueTrend])
def get_revenue_trends(
    period: str = Query("monthly", enum=["daily", "weekly", "monthly"]),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """Get revenue trends over time."""
    if period == "daily":
        period_expr = DailyProductMetric.metric_date
    elif period == "weekly":
        period_expr = func.date_trunc("week", DailyProductMetric.metric_date)
    else:
        period_expr = func.date_trunc("month", DailyProductMetric.metric_date)

    query = db.query(
        period_expr.label("period"),
        func.sum(DailyProductMetric.total_revenue).label("revenue"),
        func.sum(DailyProductMetric.total_units_sold).label("units_sold"),
        func.sum(DailyProductMetric.total_orders).label("orders"),
        func.round(func.avg(DailyProductMetric.avg_order_value), 2).label("avg_order_value"),
        func.sum(DailyProductMetric.gross_profit).label("gross_profit"),
    )

    if date_from:
        query = query.filter(DailyProductMetric.metric_date >= date_from)
    if date_to:
        query = query.filter(DailyProductMetric.metric_date <= date_to)

    results = (
        query.group_by(period_expr)
        .order_by(period_expr)
        .all()
    )

    return [
        RevenueTrend(
            period=str(r.period),
            revenue=r.revenue or 0,
            units_sold=r.units_sold or 0,
            orders=r.orders or 0,
            avg_order_value=r.avg_order_value or 0,
            gross_profit=r.gross_profit or 0,
        )
        for r in results
    ]


@router.get("/top-products", response_model=list[ProductPerformance])
def get_top_products(
    limit: int = Query(10, ge=1, le=50),
    sort_by: str = Query("revenue", enum=["revenue", "units", "profit", "margin"]),
    db: Session = Depends(get_db),
):
    """Get top performing products."""
    query = db.query(
        Product.id.label("product_id"),
        Product.sku,
        Product.name.label("product_name"),
        Category.name.label("category"),
        Product.price,
        func.coalesce(func.sum(DailyProductMetric.total_revenue), 0).label("lifetime_revenue"),
        func.coalesce(func.sum(DailyProductMetric.total_units_sold), 0).label("lifetime_units"),
        func.coalesce(func.sum(DailyProductMetric.total_orders), 0).label("lifetime_orders"),
        func.coalesce(func.sum(DailyProductMetric.gross_profit), 0).label("lifetime_profit"),
        func.coalesce(func.round(func.avg(DailyProductMetric.profit_margin), 2), 0).label("avg_profit_margin"),
    ).join(Category).outerjoin(DailyProductMetric).group_by(
        Product.id, Product.sku, Product.name, Category.name, Product.price
    )

    sort_map = {
        "revenue": "lifetime_revenue",
        "units": "lifetime_units",
        "profit": "lifetime_profit",
        "margin": "avg_profit_margin",
    }
    query = query.order_by(text(f"{sort_map[sort_by]} DESC"))

    results = query.limit(limit).all()

    return [
        ProductPerformance(
            product_id=r.product_id,
            sku=r.sku,
            product_name=r.product_name,
            category=r.category,
            price=r.price,
            lifetime_revenue=r.lifetime_revenue,
            lifetime_units=r.lifetime_units,
            lifetime_orders=r.lifetime_orders,
            lifetime_profit=r.lifetime_profit,
            avg_profit_margin=r.avg_profit_margin,
        )
        for r in results
    ]


@router.get("/category-performance", response_model=list[CategoryPerformance])
def get_category_performance(db: Session = Depends(get_db)):
    """Get performance breakdown by category."""
    results = db.query(
        Category.name.label("category"),
        func.coalesce(func.sum(DailyProductMetric.total_revenue), 0).label("total_revenue"),
        func.coalesce(func.sum(DailyProductMetric.total_units_sold), 0).label("total_units"),
        func.coalesce(func.sum(DailyProductMetric.total_orders), 0).label("total_orders"),
        func.coalesce(func.sum(DailyProductMetric.gross_profit), 0).label("gross_profit"),
        func.count(func.distinct(Product.id)).label("product_count"),
    ).join(Product, Category.id == Product.category_id
    ).outerjoin(DailyProductMetric, Product.id == DailyProductMetric.product_id
    ).group_by(Category.name
    ).order_by(text("total_revenue DESC")
    ).all()

    return [
        CategoryPerformance(
            category=r.category,
            total_revenue=r.total_revenue,
            total_units=r.total_units,
            total_orders=r.total_orders,
            gross_profit=r.gross_profit,
            product_count=r.product_count,
        )
        for r in results
    ]


@router.get("/regional-performance", response_model=list[RegionalPerformance])
def get_regional_performance(db: Session = Depends(get_db)):
    """Get performance breakdown by region."""
    results = db.query(
        Region.id.label("region_id"),
        Region.name.label("region_name"),
        Region.country,
        func.coalesce(func.sum(DailyProductMetric.total_revenue), 0).label("total_revenue"),
        func.coalesce(func.sum(DailyProductMetric.total_units_sold), 0).label("total_units"),
        func.coalesce(func.sum(DailyProductMetric.total_orders), 0).label("total_orders"),
        func.coalesce(func.sum(DailyProductMetric.gross_profit), 0).label("gross_profit"),
    ).outerjoin(DailyProductMetric, Region.id == DailyProductMetric.region_id
    ).group_by(Region.id, Region.name, Region.country
    ).order_by(text("total_revenue DESC")
    ).all()

    return [
        RegionalPerformance(
            region_id=r.region_id,
            region_name=r.region_name,
            country=r.country,
            total_revenue=r.total_revenue,
            total_units=r.total_units,
            total_orders=r.total_orders,
            gross_profit=r.gross_profit,
        )
        for r in results
    ]


@router.get("/kpis", response_model=list[KPIResponse])
def get_kpis(
    kpi_name: Optional[str] = None,
    period_type: Optional[str] = Query(None, enum=["daily", "weekly", "monthly", "yearly"]),
    dimension_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get KPI summary data."""
    query = db.query(KPISummary)

    if kpi_name:
        query = query.filter(KPISummary.kpi_name == kpi_name)
    if period_type:
        query = query.filter(KPISummary.period_type == period_type)
    if dimension_type:
        query = query.filter(KPISummary.dimension_type == dimension_type)

    return query.order_by(KPISummary.period_start.desc()).limit(100).all()


@router.get("/daily-metrics")
def get_daily_metrics(
    product_id: Optional[int] = None,
    region_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Get daily product metrics."""
    query = db.query(DailyProductMetric)

    if product_id:
        query = query.filter(DailyProductMetric.product_id == product_id)
    if region_id:
        query = query.filter(DailyProductMetric.region_id == region_id)
    if date_from:
        query = query.filter(DailyProductMetric.metric_date >= date_from)
    if date_to:
        query = query.filter(DailyProductMetric.metric_date <= date_to)

    return (
        query.order_by(DailyProductMetric.metric_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/channel-distribution", response_model=list[ChannelDistribution])
def get_channel_distribution(
    product_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get sales distribution by channel."""
    query = db.query(
        SalesTransaction.channel,
        func.sum(SalesTransaction.total_amount).label("revenue"),
        func.count(SalesTransaction.id).label("order_count")
    )

    if product_id:
        query = query.filter(SalesTransaction.product_id == product_id)

    results = query.group_by(SalesTransaction.channel).all()
    return [
        ChannelDistribution(
            channel=r.channel,
            revenue=r.revenue or 0,
            order_count=r.order_count or 0
        )
        for r in results
    ]


@router.get("/discount-impact", response_model=list[DiscountImpact])
def get_discount_impact(
    product_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get impact of discounts on order amount."""
    discount_bin = case(
        (SalesTransaction.discount_pct <= 0, '0%'),
        (SalesTransaction.discount_pct <= 5, '1-5%'),
        (SalesTransaction.discount_pct <= 10, '5-10%'),
        (SalesTransaction.discount_pct <= 15, '10-15%'),
        (SalesTransaction.discount_pct <= 20, '15-20%'),
        else_='20%+'
    ).label("discount_bin")
    
    query = db.query(
        discount_bin,
        func.avg(SalesTransaction.total_amount).label("avg_amount"),
        func.count(SalesTransaction.id).label("order_count")
    )

    if product_id:
        query = query.filter(SalesTransaction.product_id == product_id)

    results = query.group_by(discount_bin).all()
    return [
        DiscountImpact(
            discount_bin=r.discount_bin,
            avg_amount=r.avg_amount or 0,
            order_count=r.order_count or 0
        )
        for r in results
    ]
