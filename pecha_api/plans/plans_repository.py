
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from typing import Optional
from ..plans.plans_models import Plan
from fastapi import HTTPException
from starlette import status

def save_plan(db: Session, plan: Plan):
    try:
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e.orig}")


def get_plans(
    db: Session,
    search: Optional[str],
    sort_by: str,
    sort_order: str,
    skip: int,
    limit: int,
):
    # Filters
    filters = [Plan.deleted_at.is_(None)]
    if search:
        filters.append(Plan.title.ilike(f"%{search}%"))

    # Base query
    query = db.query(Plan).filter(*filters)

    # Sorting (accept enums or strings)
    sort_by_value = getattr(sort_by, "value", sort_by)
    sort_order_value = getattr(sort_order, "value", sort_order)
    sort_by_normalized = (sort_by_value or "status")
    sort_order_normalized = (sort_order_value or "asc")

    allowed_sort_by = {"status", "created_at"}
    if sort_by_normalized not in allowed_sort_by:
        sort_by_normalized = "status"
    if sort_order_normalized not in {"asc", "desc"}:
        sort_order_normalized = "asc"

    if sort_by_normalized == "status":
        order_expr = asc(Plan.status) if sort_order_normalized == "asc" else desc(Plan.status)
    elif sort_by_normalized == "created_at":
        order_expr = asc(Plan.created_at) if sort_order_normalized == "asc" else desc(Plan.created_at)
    else:
        order_expr = asc(Plan.status) if sort_order_normalized == "asc" else desc(Plan.status)

    query = query.order_by(order_expr)

    # Pagination
    rows = query.offset(skip).limit(limit).all()

    # Total count without pagination/joins
    # total = db.query(func.count(Plan.id)).filter(*filters).scalar()

    return rows
