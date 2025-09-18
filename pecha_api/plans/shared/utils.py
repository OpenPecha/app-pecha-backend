import json
import os
from typing import List
from uuid import UUID
from pecha_api.plans.plans_enums import PlanStatus, ContentType
from pecha_api.plans.plans_response_models import PlanDTO, PlanDayDTO, TaskDTO
from pecha_api.plans.shared.models import PlanListingModel, PlanModel, DayModel
from pecha_api.plans.plans_response_models import SubTaskDTO
from pecha_api.plans.shared.models import TaskModel, SubTaskModel


def load_plans_from_json() -> PlanListingModel:
    """Load plans from plan_listings.json file and return structured model"""
    json_file_path = os.path.join(
        os.path.dirname(__file__), 
        "..", 
        "mocks", 
        "plan_listings.json"
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
    tasks = []
    
    # Handle tasks conversion with error recovery
    if day_model.tasks:
        for i, task_model in enumerate(day_model.tasks):
            try:
                subtasks = convert_subtask_to_dto(task_model)
                task = TaskDTO(
                    id=UUID(task_model.id),
                    title=task_model.title,
                    estimated_time=getattr(task_model, 'estimated_time', None),
                    subtasks=subtasks
                )
                tasks.append(task)
            except (ValueError, TypeError) as e:
                # Log error and skip invalid task
                print(f"Warning: Skipping invalid task at index {i}: {e}")
                continue
    
    try:
        return PlanDayDTO(
            id=UUID(day_model.id),
            day_number=day_model.day_number,
            title=day_model.title,
            tasks=tasks
        )
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to create PlanDayDTO: {e}") from e

def convert_subtask_to_dto(task: TaskModel) -> List[SubTaskDTO]:
    if not hasattr(task, 'subtasks') or task.subtasks is None:
        return []

    subtasks = []
    
    for subtask_model in task.subtasks:
        try:
            if not all(hasattr(subtask_model, attr) for attr in ['id', 'content_type', 'content', 'display_order']):
                continue  # Skip invalid subtasks
                
            subtask = SubTaskDTO(
                id=UUID(subtask_model.id),
                content_type=ContentType(subtask_model.content_type),  # Ensure proper enum conversion
                content=subtask_model.content,
                display_order=subtask_model.display_order
            )
            subtasks.append(subtask)
        except (ValueError, TypeError) as e:
            # Log error in production, skip invalid subtask
            print(f"Warning: Skipping invalid subtask {getattr(subtask_model, 'id', 'unknown')}: {e}")
            continue
    
    return subtasks



