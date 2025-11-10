
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .plan_users_models import UserSubTaskCompletion
from fastapi import HTTPException
from starlette import status
from sqlalchemy import update
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_models import PlanSubTask
from typing import List


def save_user_sub_task_completions(db: Session, user_sub_task_completions: UserSubTaskCompletion):
    try:
        db.add(user_sub_task_completions)
        db.commit()
        db.refresh(user_sub_task_completions)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump())

def get_user_sub_task_by_user_id_and_sub_task_id(db: Session, user_id: UUID, sub_task_id: UUID) -> UserSubTaskCompletion:
    return db.query(UserSubTaskCompletion).filter(UserSubTaskCompletion.user_id == user_id, UserSubTaskCompletion.sub_task_id == sub_task_id).first()

def get_user_subtask_completions_by_user_id_and_sub_task_ids(db: Session, user_id: UUID, sub_task_ids: List[UUID]) -> List[UserSubTaskCompletion]:
    return db.query(UserSubTaskCompletion).filter(UserSubTaskCompletion.user_id == user_id, UserSubTaskCompletion.sub_task_id.in_(sub_task_ids)).all()


def save_user_sub_task_completions_bulk(db: Session, user_sub_task_completions: List[UserSubTaskCompletion]):
    try:
        db.add_all(user_sub_task_completions)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseError(error=BAD_REQUEST, message=str(e)).model_dump())


def delete_user_subtask_completion(db: Session, user_id: UUID, sub_task_ids: List[UUID]) -> None:
    try:
        db.query(UserSubTaskCompletion).filter(UserSubTaskCompletion.user_id == user_id, UserSubTaskCompletion.sub_task_id.in_(sub_task_ids)).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseError(error=BAD_REQUEST, message=str(e)).model_dump())
def get_uncompleted_user_sub_task_ids(db: Session, user_id: UUID, sub_task_ids: List[UUID]) -> List[UUID]:
    rows = (
        db.query(PlanSubTask.id)
        .filter(
            PlanSubTask.id.in_(sub_task_ids),
            ~db.query(UserSubTaskCompletion)
             .filter(
                 UserSubTaskCompletion.user_id == user_id,
                 UserSubTaskCompletion.sub_task_id == PlanSubTask.id
             )
             .exists()
        )
        .all()
    )
    return [row[0] for row in rows]