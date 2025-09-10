from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException
from starlette import status
from uuid import UUID
from pecha_api.plans.response_message import (
    AUTHOR_NOT_FOUND,
    AUTHOR_UPDATE_INVALID,
    AUTHOR_ALREADY_EXISTS,
    BAD_REQUEST,
)
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.authors.plan_author_model import Author


def save_author(db: Session, author: Author):
    try:
        db.add(author)
        db.commit()
        db.refresh(author)
        return author
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e.orig}")


def get_author_by_email(db: Session, email: str) -> Author:
    author = db.query(Author).filter(Author.email == email).first()
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=AUTHOR_NOT_FOUND)
    return author

def check_author_exists(db: Session, email: str) -> bool:
    author = db.query(Author).filter(Author.email == email).first()
    is_exists = True if author else False
    return is_exists


def get_author_by_id(db: Session, author_id: UUID) -> Author:
    author = db.query(Author).filter(Author.id == author_id).first()
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=AUTHOR_NOT_FOUND)
    return author


def update_author(db: Session, author: Author) -> Author:
    try:
        db.add(author)
        db.commit()
        db.refresh(author)
        return author
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=AUTHOR_UPDATE_INVALID)

