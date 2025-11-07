from uuid import UUID
from sqlalchemy.orm import Session
from typing import List
from .plan_users_model import UserTaskCompletion
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST


def save_user_task_completion(db: Session, user_task_completion: UserTaskCompletion):
    try:
        db.add(user_task_completion)
        db.commit()
        db.refresh(user_task_completion)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump())
    db.commit()
    db.refresh(user_task_completion)


def get_user_task_completions_by_user_id_and_task_ids(db: Session, user_id: UUID, task_ids: List[UUID]) -> List[UserTaskCompletion]:
    return db.query(UserTaskCompletion).filter(UserTaskCompletion.user_id == user_id, UserTaskCompletion.task_id.in_(task_ids)).all()