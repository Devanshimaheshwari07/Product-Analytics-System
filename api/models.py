"""
SQLAlchemy ORM models mapping to all database tables.
"""
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, Date, DateTime, Text,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    products = relationship("Product", back_populates="category")


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    country = Column(String(100), nullable=False)
    timezone = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    sales = relationship("SalesTransaction", back_populates="region")
    metrics = relationship("DailyProductMetric", back_populates="region")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    launch_date = Column(Date)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    category = relationship("Category", back_populates="products")
    sales = relationship("SalesTransaction", back_populates="product")
    metrics = relationship("DailyProductMetric", back_populates="product")


class SalesTransaction(Base):
    __tablename__ = "sales_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(36))
    product_id = Column(Integer, ForeignKey("products.id"))
    region_id = Column(Integer, ForeignKey("regions.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_pct = Column(Numeric(5, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    channel = Column(String(50), default="online")
    customer_segment = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="sales")
    region = relationship("Region", back_populates="sales")


class DailyProductMetric(Base):
    __tablename__ = "daily_product_metrics"
    __table_args__ = (
        UniqueConstraint("product_id", "region_id", "metric_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    region_id = Column(Integer, ForeignKey("regions.id"))
    metric_date = Column(Date, nullable=False)
    total_revenue = Column(Numeric(14, 2), default=0)
    total_units_sold = Column(Integer, default=0)
    total_orders = Column(Integer, default=0)
    avg_order_value = Column(Numeric(10, 2), default=0)
    avg_discount_pct = Column(Numeric(5, 2), default=0)
    gross_profit = Column(Numeric(14, 2), default=0)
    profit_margin = Column(Numeric(5, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="metrics")
    region = relationship("Region", back_populates="metrics")


class KPISummary(Base):
    __tablename__ = "kpi_summary"
    __table_args__ = (
        UniqueConstraint(
            "kpi_name", "period_type", "period_start",
            "dimension_type", "dimension_value"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    kpi_name = Column(String(100), nullable=False)
    kpi_value = Column(Numeric(16, 4))
    kpi_unit = Column(String(20))
    period_type = Column(String(20), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    dimension_type = Column(String(50))
    dimension_value = Column(String(100))
    previous_value = Column(Numeric(16, 4))
    change_pct = Column(Numeric(8, 2))
    created_at = Column(DateTime, server_default=func.now())
