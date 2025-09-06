
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

    # Sorting
    sort_by_normalized = (sort_by or "title").lower()
    sort_order_normalized = (sort_order or "asc").lower()

    if sort_by_normalized not in {"title", "created_at"}:
        sort_by_normalized = "title"
    if sort_order_normalized not in {"asc", "desc"}:
        sort_order_normalized = "asc"

    if sort_by_normalized == "title":
        order_expr = asc(Plan.title) if sort_order_normalized == "asc" else desc(Plan.title)
    elif sort_by_normalized == "created_at":
        order_expr = asc(Plan.created_at) if sort_order_normalized == "asc" else desc(Plan.created_at)
    else:
        order_expr = asc(Plan.title) if sort_order_normalized == "asc" else desc(Plan.title)

    query = query.order_by(order_expr)

    # Pagination
    rows = query.offset(skip).limit(limit).all()

    # Total count without pagination/joins
    total = db.query(func.count(Plan.id)).filter(*filters).scalar()

    return rows, int(total or 0)
