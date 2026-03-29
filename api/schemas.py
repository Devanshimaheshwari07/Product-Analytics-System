"""
Pydantic schemas for API request/response serialization.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ─── Category Schemas ─────────────────────────────────────────
class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Region Schemas ───────────────────────────────────────────
class RegionResponse(BaseModel):
    id: int
    name: str
    country: str
    timezone: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Product Schemas ──────────────────────────────────────────
class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    category_id: int
    price: Decimal
    cost: Decimal
    stock_quantity: int
    is_active: bool
    launch_date: Optional[date] = None
    description: Optional[str] = None
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]


# ─── Sales Schemas ────────────────────────────────────────────
class SalesTransactionResponse(BaseModel):
    id: int
    transaction_id: Optional[str] = None
    product_id: int
    region_id: int
    quantity: int
    unit_price: Decimal
    discount_pct: Decimal
    total_amount: Decimal
    transaction_date: datetime
    channel: str
    customer_segment: Optional[str] = None

    class Config:
        from_attributes = True


class SalesAggregation(BaseModel):
    period: str
    total_revenue: Decimal
    total_units: int
    total_orders: int
    avg_order_value: Decimal


class SalesListResponse(BaseModel):
    total: int
    items: List[SalesTransactionResponse]


# ─── Analytics / KPI Schemas ─────────────────────────────────
class KPIResponse(BaseModel):
    kpi_name: str
    kpi_value: Optional[Decimal] = None
    kpi_unit: Optional[str] = None
    period_type: str
    period_start: date
    period_end: date
    dimension_type: Optional[str] = None
    dimension_value: Optional[str] = None
    previous_value: Optional[Decimal] = None
    change_pct: Optional[Decimal] = None

    class Config:
        from_attributes = True


class DailyMetricResponse(BaseModel):
    product_id: int
    region_id: int
    metric_date: date
    total_revenue: Decimal
    total_units_sold: int
    total_orders: int
    avg_order_value: Decimal
    avg_discount_pct: Decimal
    gross_profit: Decimal
    profit_margin: Decimal

    class Config:
        from_attributes = True


class ProductPerformance(BaseModel):
    product_id: int
    sku: str
    product_name: str
    category: str
    price: Decimal
    lifetime_revenue: Decimal
    lifetime_units: int
    lifetime_orders: int
    lifetime_profit: Decimal
    avg_profit_margin: Decimal


class RegionalPerformance(BaseModel):
    region_id: int
    region_name: str
    country: str
    total_revenue: Decimal
    total_units: int
    total_orders: int
    gross_profit: Decimal


class CategoryPerformance(BaseModel):
    category: str
    total_revenue: Decimal
    total_units: int
    total_orders: int
    gross_profit: Decimal
    product_count: int


class RevenueTrend(BaseModel):
    period: str
    revenue: Decimal
    units_sold: int
    orders: int
    avg_order_value: Decimal
    gross_profit: Decimal


class OverviewKPIs(BaseModel):
    total_revenue: Decimal
    total_orders: int
    total_units_sold: int
    avg_order_value: Decimal
    gross_profit: Decimal
    avg_profit_margin: Decimal
    total_products: int
    active_regions: int
