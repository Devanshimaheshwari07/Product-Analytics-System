"""
Products router — CRUD and listing endpoints with filtering.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from database import get_db
from models import Product, Category
from schemas import ProductResponse, ProductListResponse

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    category: Optional[str] = Query(None, description="Filter by category name"),
    is_active: Optional[bool] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    search: Optional[str] = Query(None, description="Search product name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Product).options(joinedload(Product.category))

    if category:
        query = query.join(Category).filter(Category.name.ilike(f"%{category}%"))
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return ProductListResponse(total=total, items=items)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    return product
