"""
Sales router — transactions listing with aggregation support.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date

from database import get_db
from models import SalesTransaction
from schemas import SalesTransactionResponse, SalesListResponse, SalesAggregation

router = APIRouter(prefix="/api/v1/sales", tags=["Sales"])


@router.get("", response_model=SalesListResponse)
def list_sales(
    product_id: Optional[int] = None,
    region_id: Optional[int] = None,
    channel: Optional[str] = None,
    customer_segment: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(SalesTransaction)

    if product_id:
        query = query.filter(SalesTransaction.product_id == product_id)
    if region_id:
        query = query.filter(SalesTransaction.region_id == region_id)
    if channel:
        query = query.filter(SalesTransaction.channel == channel)
    if customer_segment:
        query = query.filter(SalesTransaction.customer_segment == customer_segment)
    if date_from:
        query = query.filter(SalesTransaction.transaction_date >= date_from)
    if date_to:
        query = query.filter(SalesTransaction.transaction_date <= date_to)

    total = query.count()
    items = (
        query.order_by(SalesTransaction.transaction_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return SalesListResponse(total=total, items=items)


@router.get("/aggregate", response_model=list[SalesAggregation])
def aggregate_sales(
    group_by: str = Query("monthly", enum=["daily", "weekly", "monthly"]),
    product_id: Optional[int] = None,
    region_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """Aggregate sales by time period."""
    if group_by == "daily":
        period_expr = func.date(SalesTransaction.transaction_date)
    elif group_by == "weekly":
        period_expr = func.date_trunc("week", SalesTransaction.transaction_date)
    else:
        period_expr = func.date_trunc("month", SalesTransaction.transaction_date)

    query = db.query(
        period_expr.label("period"),
        func.sum(SalesTransaction.total_amount).label("total_revenue"),
        func.sum(SalesTransaction.quantity).label("total_units"),
        func.count().label("total_orders"),
        func.round(func.avg(SalesTransaction.total_amount), 2).label("avg_order_value"),
    )

    if product_id:
        query = query.filter(SalesTransaction.product_id == product_id)
    if region_id:
        query = query.filter(SalesTransaction.region_id == region_id)
    if date_from:
        query = query.filter(SalesTransaction.transaction_date >= date_from)
    if date_to:
        query = query.filter(SalesTransaction.transaction_date <= date_to)

    results = (
        query.group_by(period_expr)
        .order_by(period_expr)
        .all()
    )

    return [
        SalesAggregation(
            period=str(r.period),
            total_revenue=r.total_revenue,
            total_units=r.total_units,
            total_orders=r.total_orders,
            avg_order_value=r.avg_order_value or 0,
        )
        for r in results
    ]


@router.get("/channels")
def get_channels(db: Session = Depends(get_db)):
    """Get distinct sales channels."""
    results = db.query(SalesTransaction.channel).distinct().all()
    return [r[0] for r in results]


@router.get("/segments")
def get_segments(db: Session = Depends(get_db)):
    """Get distinct customer segments."""
    results = db.query(SalesTransaction.customer_segment).distinct().all()
    return [r[0] for r in results if r[0]]
