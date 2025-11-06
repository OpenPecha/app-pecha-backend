from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .plan_users_model import UserSubTaskCompletion
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_models import PlanSubTask

def save_user_sub_task_completions(db: Session, user_sub_task_completions: UserSubTaskCompletion):
    try:
        db.add(user_sub_task_completions)
        db.commit()
        db.refresh(user_sub_task_completions)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump())
