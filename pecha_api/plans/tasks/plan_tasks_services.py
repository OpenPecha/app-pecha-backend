from uuid import UUID
from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.tasks.plan_tasks_repository import create_task
from pecha_api.plans.authors.plan_author_service import validate_and_extract_author_details


async def create_new_task(token: str, create_task_request: CreateTaskRequest, plan_id: UUID, day_id: UUID) -> TaskDTO:
    author = validate_and_extract_author_details(token=token)
    return create_task(
        create_task_request=create_task_request,
        plan_id=plan_id,
        day_id=day_id,
        created_by=author.email,
    )