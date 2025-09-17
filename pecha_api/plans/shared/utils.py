import json
import os
from uuid import UUID
from pecha_api.plans.plans_enums import PlanStatus, ContentType
from pecha_api.plans.plans_response_models import PlanDTO, PlanDayDTO, TaskDTO
from pecha_api.plans.shared.models import PlanListingModel, PlanModel, DayModel


def load_plans_from_json() -> PlanListingModel:
    """Load plans from plan_listing.json file and return structured model"""
    json_file_path = os.path.join(
        os.path.dirname(__file__), 
        "..", 
        "mocks", 
        "plan_listing.json"
    )
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Parse JSON directly into our model
        plan_listing = PlanListingModel(**data)
        return plan_listing
        
    except FileNotFoundError:
        # Fallback to empty model if file not found
        return PlanListingModel(plans=[], skip=0, limit=0, total=0)
    except (json.JSONDecodeError, ValueError) as e:
        # Log error and return empty model
        print(f"Error loading plans from JSON: {e}")
        return PlanListingModel(plans=[], skip=0, limit=0, total=0)


def convert_plan_model_to_dto(plan_model: PlanModel) -> PlanDTO:
    """Convert PlanModel to PlanDTO"""
    return PlanDTO(
        id=UUID(plan_model.id),
        title=plan_model.title,
        description=plan_model.description,
        image_url=plan_model.image_url,
        total_days=plan_model.total_days,
        status=PlanStatus(plan_model.status),
        subscription_count=plan_model.subscription_count
    )


def convert_day_model_to_dto(day_model: DayModel) -> PlanDayDTO:
    """Convert DayModel to PlanDayDTO"""
    tasks = []
    for task_model in day_model.tasks:
        task = TaskDTO(
            id=UUID(task_model.id),
            title=task_model.title,
            description=task_model.description,
            content_type=ContentType(task_model.content_type),
            content=task_model.content,
            estimated_time=task_model.estimated_time
        )
        tasks.append(task)
    
    return PlanDayDTO(
        id=UUID(day_model.id),
        day_number=day_model.day_number,
        title=day_model.title,
        tasks=tasks
    )
