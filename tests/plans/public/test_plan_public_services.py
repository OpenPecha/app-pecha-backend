import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from starlette import status

from pecha_api.plans.public.plan_service import get_plan_days, get_plan_day_details
from pecha_api.plans.public.plan_response_models import PlanDaysResponse, PlanDayDTO, TaskDTO, SubTaskDTO
from pecha_api.error_contants import ErrorConstants
from pecha_api.plans.plans_enums import ContentType
from pecha_api.plans.response_message import BAD_REQUEST, PLAN_DAY_NOT_FOUND


def _mock_session_local(mock_session_local):
    """Helper function to mock SessionLocal context manager"""
    mock_db_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db_session
    mock_session_local.return_value.__exit__.return_value = False
    return mock_db_session


@pytest.mark.asyncio
async def test_get_plan_days_success():
    """Test successful retrieval of plan days"""
    token = "valid_token_123"
    plan_id = uuid.uuid4()
    
    mock_plan = MagicMock()
    mock_plan.id = plan_id
    mock_plan.title = "Test Plan"
    
    mock_day_1 = MagicMock()
    mock_day_1.id = uuid.uuid4()
    mock_day_1.day_number = 1
    
    mock_day_2 = MagicMock()
    mock_day_2.id = uuid.uuid4()
    mock_day_2.day_number = 2
    
    mock_plan_days = [mock_day_1, mock_day_2]
    
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()
    mock_user.email = "test@example.com"

    with patch("pecha_api.plans.public.plan_service.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.public.plan_service.validate_and_extract_user_details") as mock_validate_user, \
         patch("pecha_api.plans.public.plan_service.get_plan_by_id") as mock_get_plan, \
         patch("pecha_api.plans.public.plan_service.get_days_by_plan_id") as mock_get_days:
        
        db_session = _mock_session_local(mock_session_local)
        mock_validate_user.return_value = mock_user
        mock_get_plan.return_value = mock_plan
        mock_get_days.return_value = mock_plan_days

        response = await get_plan_days(token=token, plan_id=plan_id)

        mock_validate_user.assert_called_once_with(token=token)
        
        mock_get_plan.assert_called_once_with(db=db_session, plan_id=plan_id)
        mock_get_days.assert_called_once_with(db=db_session, plan_id=plan_id)

        assert isinstance(response, PlanDaysResponse)
        assert len(response.days) == 2
        
        assert response.days[0].id == str(mock_day_1.id)
        assert response.days[0].day_number == 1
        assert response.days[1].id == str(mock_day_2.id)
        assert response.days[1].day_number == 2


@pytest.mark.asyncio
async def test_get_plan_days_empty_days():
    """Test retrieval when plan has no days"""
    token = "valid_token_456"
    plan_id = uuid.uuid4()
    
    mock_plan = MagicMock()
    mock_plan.id = plan_id
    mock_plan.title = "Empty Plan"
    
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()

    with patch("pecha_api.plans.public.plan_service.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.public.plan_service.validate_and_extract_user_details") as mock_validate_user, \
         patch("pecha_api.plans.public.plan_service.get_plan_by_id") as mock_get_plan, \
         patch("pecha_api.plans.public.plan_service.get_days_by_plan_id") as mock_get_days:
        
        db_session = _mock_session_local(mock_session_local)
        mock_validate_user.return_value = mock_user
        mock_get_plan.return_value = mock_plan
        mock_get_days.return_value = []

        response = await get_plan_days(token=token, plan_id=plan_id)

        mock_validate_user.assert_called_once_with(token=token)
        mock_get_plan.assert_called_once_with(db=db_session, plan_id=plan_id)
        mock_get_days.assert_called_once_with(db=db_session, plan_id=plan_id)

        assert isinstance(response, PlanDaysResponse)
        assert len(response.days) == 0


@pytest.mark.asyncio
async def test_get_plan_days_plan_not_found():
    """Test when plan does not exist"""
    token = "valid_token_789"
    plan_id = uuid.uuid4()
    
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()

    with patch("pecha_api.plans.public.plan_service.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.public.plan_service.validate_and_extract_user_details") as mock_validate_user, \
         patch("pecha_api.plans.public.plan_service.get_plan_by_id") as mock_get_plan:
        
        db_session = _mock_session_local(mock_session_local)
        mock_validate_user.return_value = mock_user
        mock_get_plan.return_value = None 

        with pytest.raises(HTTPException) as exc_info:
            await get_plan_days(token=token, plan_id=plan_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.PLAN_NOT_FOUND

        mock_validate_user.assert_called_once_with(token=token)
        mock_get_plan.assert_called_once_with(db=db_session, plan_id=plan_id)

@pytest.mark.asyncio
async def test_get_plan_day_details_success():
    """Test successful retrieval of plan day details with tasks and subtasks"""
    token = "valid_token_123"
    plan_id = uuid.uuid4()
    day_number = 1
    
    mock_subtask_1 = MagicMock()
    mock_subtask_1.id = uuid.uuid4()
    mock_subtask_1.content_type = ContentType.TEXT
    mock_subtask_1.content = "Subtask content 1"
    mock_subtask_1.display_order = 1
    
    mock_task = MagicMock()
    mock_task.id = uuid.uuid4()
    mock_task.title = "Test Task"
    mock_task.estimated_time = 30
    mock_task.display_order = 1
    mock_task.sub_tasks = [mock_subtask_1]
    
    mock_plan_item = MagicMock()
    mock_plan_item.id = uuid.uuid4()
    mock_plan_item.day_number = day_number
    mock_plan_item.tasks = [mock_task]
    
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()
    mock_user.email = "test@example.com"

    with patch("pecha_api.plans.public.plan_service.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.public.plan_service.validate_and_extract_user_details") as mock_validate_user, \
         patch("pecha_api.plans.public.plan_service.get_plan_day_with_tasks_and_subtasks") as mock_get_plan_day:
        
        db_session = _mock_session_local(mock_session_local)
        mock_validate_user.return_value = mock_user
        mock_get_plan_day.return_value = mock_plan_item

        response = await get_plan_day_details(token=token, plan_id=plan_id, day_number=day_number)

        mock_validate_user.assert_called_once_with(token=token)
        mock_get_plan_day.assert_called_once_with(db=db_session, plan_id=plan_id, day_number=day_number)

        assert isinstance(response, PlanDayDTO)
        assert response.id == mock_plan_item.id
        assert response.day_number == day_number
        assert len(response.tasks) == 1
        
        task = response.tasks[0]
        assert task.id == mock_task.id
        assert task.title == "Test Task"
        assert task.estimated_time == 30
        assert task.display_order == 1
        assert len(task.subtasks) == 1
        
        assert task.subtasks[0].id == mock_subtask_1.id
        assert task.subtasks[0].content_type == ContentType.TEXT
        assert task.subtasks[0].content == "Subtask content 1"
        assert task.subtasks[0].display_order == 1