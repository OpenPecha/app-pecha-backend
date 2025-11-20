from uuid import UUID
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST, PLAN_NOT_FOUND, DUPLICATE_DAY_NUMBERS
from .plan_items_repository import save_plan_item, get_last_day_number, get_day_by_plan_day_id, delete_day_by_id, get_days_by_plan_id, update_day_by_id, update_days_in_bulk_by_plan_id, get_days_by_day_ids
from pecha_api.plans.cms.cms_plans_repository import get_plan_by_id, get_plan_by_id_and_created_by
from .plan_items_models import PlanItem
from pecha_api.plans.plans_models import Plan
from pecha_api.plans.authors.plan_authors_model import Author
from .plan_items_response_models import ItemDTO, ReorderDaysRequest
from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from pecha_api.db.database import SessionLocal

def create_plan_item(token: str, plan_id: UUID) -> ItemDTO:
    current_author = validate_and_extract_author_details(token=token)

    with SessionLocal() as db_session:
        plan = _get_author_plan(plan_id=plan_id, current_author=current_author,is_admin=current_author.is_admin)
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
        plan = _get_author_plan(plan_id=plan_id, current_author=current_author,is_admin=current_author.is_admin)

        item = get_day_by_plan_day_id(db=db_session, plan_id=plan.id, day_id=day_id)
        delete_day_by_id(db=db_session, plan_id=plan.id, day_id=item.id)
        _reorder_day_display_order(db=db_session, plan_id=plan.id)

def update_plans_day_number(token: str, plan_id: UUID, reorder_days_request: ReorderDaysRequest) -> None:
    current_author = validate_and_extract_author_details(token=token)
    with SessionLocal() as db_session:
        plan = _get_author_plan(plan_id=plan_id, current_author=current_author,is_admin=current_author.is_admin)
        _check_duplicate_day_number_payload(payload=reorder_days_request)
        update_days_in_bulk_by_plan_id(db=db_session, plan_id=plan.id, days=reorder_days_request.days)

def _reorder_day_display_order(db: SessionLocal(), plan_id: UUID) -> None:

    items = get_days_by_plan_id(db=db, plan_id=plan_id)
    sorted_items = sorted(items, key=lambda x: x.day_number)
    
    for index, item in enumerate(sorted_items, start=1):
        update_day_by_id(db=db, plan_id=plan_id, day_id=item.id, day_number=index)


def _get_author_plan(plan_id: UUID, current_author: Author, is_admin: bool) -> Plan:
    with SessionLocal() as db_session:
        plan = get_plan_by_id_and_created_by(db=db_session, plan_id=plan_id, created_by=current_author.email, is_admin=is_admin)
        if not is_admin and plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=PLAN_NOT_FOUND).model_dump())
        return plan

def _check_duplicate_day_number_payload(payload: ReorderDaysRequest) -> None:

    #store the day numbers which is unique using set function...
    day_numbers = set([day.day_number for day in payload.days])
    if len(day_numbers) != len(payload.days):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseError(error=BAD_REQUEST, message=DUPLICATE_DAY_NUMBERS).model_dump())