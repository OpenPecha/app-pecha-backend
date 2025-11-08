import uuid
import pytest
from unittest.mock import patch, AsyncMock

from pecha_api.plans.public.plan_response_models import PlanDaysResponse, PlanDayBasic, PlanDayDTO, TaskDTO, SubTaskDTO
from pecha_api.plans.public.plan_views import get_plan_days_list, get_plan_day_content
from pecha_api.plans.plans_enums import ContentType


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_get_plan_days_list_success():
    """Test successful retrieval of plan days list"""
    creds = _Creds(token="valid_token_123")
    plan_id = uuid.uuid4()
    
    expected_days = [
        PlanDayBasic(id=str(uuid.uuid4()), day_number=1),
        PlanDayBasic(id=str(uuid.uuid4()), day_number=2),
    ]
    expected_response = PlanDaysResponse(days=expected_days)

    with patch(
        "pecha_api.plans.public.plan_views.get_plan_days",
        return_value=expected_response,
        new_callable=AsyncMock,
    ) as mock_service:
        response = await get_plan_days_list(
            authentication_credential=creds,
            plan_id=plan_id
        )

        mock_service.assert_called_once_with(
            token="valid_token_123",
            plan_id=plan_id
        )

        assert response == expected_response
        assert len(response.days) == 2
        assert response.days[0].day_number == 1
        assert response.days[1].day_number == 2


@pytest.mark.asyncio
async def test_get_plan_days_list_empty_days():
    """Test retrieval when plan has no days"""
    creds = _Creds(token="valid_token_456")
    plan_id = uuid.uuid4()
    
    expected_response = PlanDaysResponse(days=[])

    with patch(
        "pecha_api.plans.public.plan_views.get_plan_days",
        return_value=expected_response,
        new_callable=AsyncMock,
    ) as mock_service:
        response = await get_plan_days_list(
            authentication_credential=creds,
            plan_id=plan_id
        )

        mock_service.assert_called_once_with(
            token="valid_token_456",
            plan_id=plan_id
        )

        assert response == expected_response
        assert len(response.days) == 0

@pytest.mark.asyncio
async def test_get_plan_day_content_success():
    """Test successful retrieval of plan day content"""
    creds = _Creds(token="valid_token_123")
    plan_id = uuid.uuid4()
    day_number = 1
    
    expected_subtask = SubTaskDTO(
        id=uuid.uuid4(),
        content_type=ContentType.TEXT,
        content="Test subtask content",
        display_order=1
    )
    
    expected_task = TaskDTO(
        id=uuid.uuid4(),
        title="Test Task",
        estimated_time=30,
        display_order=1,
        subtasks=[expected_subtask]
    )
    
    expected_response = PlanDayDTO(
        id=uuid.uuid4(),
        day_number=day_number,
        tasks=[expected_task]
    )

    with patch(
        "pecha_api.plans.public.plan_views.get_plan_day_details",
        return_value=expected_response,
        new_callable=AsyncMock,
    ) as mock_service:
        response = await get_plan_day_content(
            authentication_credential=creds,
            plan_id=plan_id,
            day_number=day_number
        )

        mock_service.assert_called_once_with(
            token="valid_token_123",
            plan_id=plan_id,
            day_number=day_number
        )

        assert response == expected_response
        assert response.id == expected_response.id
        assert response.day_number == day_number
        assert len(response.tasks) == 1
        
        task = response.tasks[0]
        assert task.id == expected_task.id
        assert task.title == "Test Task"
        assert task.estimated_time == 30
        assert task.display_order == 1
        assert len(task.subtasks) == 1
        
        subtask = task.subtasks[0]
        assert subtask.id == expected_subtask.id
        assert subtask.content_type == ContentType.TEXT
        assert subtask.content == "Test subtask content"
        assert subtask.display_order == 1


@pytest.mark.asyncio
async def test_get_plan_day_content_no_tasks():
    """Test retrieval of plan day with no tasks"""
    creds = _Creds(token="valid_token_456")
    plan_id = uuid.uuid4()
    day_number = 2
    
    expected_response = PlanDayDTO(
        id=uuid.uuid4(),
        day_number=day_number,
        tasks=[]
    )

    with patch(
        "pecha_api.plans.public.plan_views.get_plan_day_details",
        return_value=expected_response,
        new_callable=AsyncMock,
    ) as mock_service:
        response = await get_plan_day_content(
            authentication_credential=creds,
            plan_id=plan_id,
            day_number=day_number
        )

        mock_service.assert_called_once_with(
            token="valid_token_456",
            plan_id=plan_id,
            day_number=day_number
        )

        assert response == expected_response
        assert response.id == expected_response.id
        assert response.day_number == day_number
        assert len(response.tasks) == 0