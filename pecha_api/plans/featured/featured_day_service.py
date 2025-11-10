import random
from fastapi import HTTPException, status
from ...db.database import SessionLocal
from .featured_day_repository import get_all_featured_plan_days
from .featured_day_response_model import PlanDayDTO, TaskDTO, SubTaskDTO
import logging

logger = logging.getLogger(__name__)


def get_featured_day_service() -> PlanDayDTO:
    with SessionLocal() as db:
        featured_days = get_all_featured_plan_days(db)
        
        if not featured_days:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No featured plans with days found"
            )
        
        random_day_item = random.choice(featured_days)
        
        tasks = []
        for task in sorted(random_day_item.tasks, key=lambda t: t.display_order):
            subtasks = [
                SubTaskDTO(
                    id=subtask.id,
                    content_type=subtask.content_type,
                    content=subtask.content,
                    display_order=subtask.display_order
                )
                for subtask in sorted(task.sub_tasks, key=lambda st: st.display_order)
            ]
            
            tasks.append(
                TaskDTO(
                    id=task.id,
                    title=task.title,
                    estimated_time=task.estimated_time,
                    display_order=task.display_order,
                    subtasks=subtasks
                )
            )
        
        return PlanDayDTO(
            id=random_day_item.id,
            day_number=random_day_item.day_number,
            tasks=tasks
        )