from fastapi import HTTPException, status
from ...db.database import SessionLocal
from .featured_day_repository import get_all_featured_plan_days
from .featured_day_response_model import PlanDayDTO, TaskDTO, SubTaskDTO
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def get_featured_day_service(language: str) -> PlanDayDTO:
    with SessionLocal() as db:
        language_upper = language.upper()
        
        featured_days = get_all_featured_plan_days(db, language=language_upper)
        
        if not featured_days:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No featured plans with days found")
        
        today = datetime.now().date()
        index = today.toordinal() % len(featured_days)
        selected_day_item = featured_days[index]
                
        tasks = []
        for task in sorted(selected_day_item.tasks, key=lambda t: t.display_order):
            subtasks = [
                SubTaskDTO(id=subtask.id,content_type=subtask.content_type,content=subtask.content,display_order=subtask.display_order)
                for subtask in sorted(task.sub_tasks, key=lambda st: st.display_order)
            ]
            
            tasks.append(TaskDTO(id=task.id,title=task.title,estimated_time=task.estimated_time,display_order=task.display_order,subtasks=subtasks))
            
        
        return PlanDayDTO(id=selected_day_item.id,day_number=selected_day_item.day_number,tasks=tasks)