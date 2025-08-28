from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pecha_api.plans.plan_models import Author
from fastapi import HTTPException
from starlette import status


def save_user(db: Session, author: Author):
    try:
        db.add(author)
        db.commit()
        db.refresh(author)
        return author
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

