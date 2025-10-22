from uuid import UUID
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST, PLAN_NOT_FOUND
from .plan_items_repository import save_plan_item, get_last_day_number, get_day_by_plan_day_id, delete_day_by_id, get_days_by_plan_id, update_day_by_id
from pecha_api.plans.cms.cms_plans_repository import get_plan_by_id
from .plan_items_models import PlanItem
from .plan_items_response_models import ItemDTO
from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from pecha_api.db.database import SessionLocal

def create_plan_item(token: str, plan_id: UUID) -> ItemDTO:
    current_author = validate_and_extract_author_details(token=token)

    with SessionLocal() as db_session:
        plan = get_plan_by_id(db=db_session, plan_id=plan_id)
        last_day_number = get_last_day_number(db=db_session, plan_id=plan.id)
        new_day_number = last_day_number + 1
        plan_item = PlanItem(
            plan_id=plan.id,
            day_number=new_day_number,
            created_by=current_author.email
        )
        saved_item = save_plan_item(db=db_session, plan_item=plan_item)

    return ItemDTO(
        id=saved_item.id,
        plan_id=saved_item.plan_id,
        day_number=saved_item.day_number
    )

def delete_plan_day_by_id(token: str, plan_id: UUID, day_id: UUID) -> None:
    current_author = validate_and_extract_author_details(token=token)

    with SessionLocal() as db_session:
        plan = get_plan_by_id(db=db_session, plan_id=plan_id, created_by=current_author.email)
        if plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=PLAN_NOT_FOUND).model_dump())
        item = get_day_by_plan_day_id(db=db_session, plan_id=plan.id, day_id=day_id)
        delete_day_by_id(db=db_session, plan_id=plan.id, day_id=item.id)
        _reorder_day_display_order(db=db_session, plan_id=plan.id)



def _reorder_day_display_order(db: SessionLocal(), plan_id: UUID) -> None:

    items = get_days_by_plan_id(db=db, plan_id=plan_id)
    sorted_items = sorted(items, key=lambda x: x.day_number)
    
    for index, item in enumerate(sorted_items, start=1):
        update_day_by_id(db=db, plan_id=plan_id, day_id=item.id, day_number=index)


