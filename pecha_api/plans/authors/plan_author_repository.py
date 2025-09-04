
from sqlalchemy.orm import Session
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.authors.plan_author_model import Author


def get_author_by_email(db: Session, email: str):
    user = db.query(Author).filter(Author.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user