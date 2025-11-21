from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List
from ..plans_models import Plan
from ..items.plan_items_models import PlanItem
from ..tasks.plan_tasks_models import PlanTask
from ..tasks.sub_tasks.plan_sub_tasks_models import PlanSubTask
from ..plans_enums import PlanStatus

def get_all_featured_plan_days(db: Session, language: str = "EN") -> List[PlanItem]:
   
    query = (
        db.query(PlanItem)
        .join(Plan, PlanItem.plan_id == Plan.id)
        .options(
            joinedload(PlanItem.tasks)
            .joinedload(PlanTask.sub_tasks)
        )
        .filter(
            and_(
                Plan.featured == True,
                Plan.status == PlanStatus.PUBLISHED,
                Plan.language == language
            )
        )
        .all()
    )
    
    return query
