from uuid import UUID
from .plan_items_repository import save_plan_item, get_last_day_number
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