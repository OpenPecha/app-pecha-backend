import pytest
from uuid import uuid4
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette import status

from pecha_api.app import api
from pecha_api.plans.featured.featured_day_response_model import PlanDayDTO, TaskDTO, SubTaskDTO
from pecha_api.plans.plans_enums import ContentType


client = TestClient(api)


@pytest.fixture
def sample_subtask_dto():
    """Sample subtask DTO for testing."""
    return SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.TEXT,
        content="Practice deep breathing for 5 minutes",
        display_order=1
    )


@pytest.fixture
def sample_task_dto(sample_subtask_dto):
    """Sample task DTO for testing."""
    return TaskDTO(
        id=uuid4(),
        title="Morning Meditation",
        estimated_time=30,
        display_order=1,
        subtasks=[sample_subtask_dto]
    )


@pytest.fixture
def sample_plan_day_dto(sample_task_dto):
    """Sample plan day DTO for testing."""
    return PlanDayDTO(
        id=uuid4(),
        day_number=15,
        tasks=[sample_task_dto]
    )


@pytest.fixture
def sample_plan_day_with_multiple_tasks():
    """Sample plan day with multiple tasks and subtasks."""
    subtask1 = SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.TEXT,
        content="Read introduction",
        display_order=1
    )
    subtask2 = SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.VIDEO,
        content="https://video.url/meditation-guide",
        display_order=2
    )
    
    task1 = TaskDTO(
        id=uuid4(),
        title="Morning Practice",
        estimated_time=20,
        display_order=1,
        subtasks=[subtask1, subtask2]
    )
    
    task2 = TaskDTO(
        id=uuid4(),
        title="Evening Reflection",
        estimated_time=15,
        display_order=2,
        subtasks=[]
    )
    
    return PlanDayDTO(
        id=uuid4(),
        day_number=7,
        tasks=[task1, task2]
    )


@pytest.mark.asyncio
async def test_get_featured_day_success(sample_plan_day_dto):
    """Test successful retrieval of featured day."""
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=sample_plan_day_dto) as mock_service:
        response = client.get("/plans/featured/day")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "id" in data
        assert "day_number" in data
        assert "tasks" in data
        
        assert data["day_number"] == 15
        assert len(data["tasks"]) == 1
        
        task = data["tasks"][0]
        assert "id" in task
        assert task["title"] == "Morning Meditation"
        assert task["estimated_time"] == 30
        assert task["display_order"] == 1
        assert "subtasks" in task
        assert len(task["subtasks"]) == 1
        
        subtask = task["subtasks"][0]
        assert "id" in subtask
        assert subtask["content_type"] == ContentType.TEXT.value
        assert subtask["content"] == "Practice deep breathing for 5 minutes"
        assert subtask["display_order"] == 1
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_with_multiple_tasks(sample_plan_day_with_multiple_tasks):
    """Test retrieval of featured day with multiple tasks and subtasks."""
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=sample_plan_day_with_multiple_tasks) as mock_service:
        response = client.get("/plans/featured/day")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["day_number"] == 7
        assert len(data["tasks"]) == 2
        
        task1 = data["tasks"][0]
        assert task1["title"] == "Morning Practice"
        assert task1["estimated_time"] == 20
        assert task1["display_order"] == 1
        assert len(task1["subtasks"]) == 2
        
        assert task1["subtasks"][0]["content_type"] == ContentType.TEXT.value
        assert task1["subtasks"][1]["content_type"] == ContentType.VIDEO.value
        
        task2 = data["tasks"][1]
        assert task2["title"] == "Evening Reflection"
        assert task2["estimated_time"] == 15
        assert task2["display_order"] == 2
        assert len(task2["subtasks"]) == 0
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_with_empty_tasks():
    plan_day_no_tasks = PlanDayDTO(
        id=uuid4(),
        day_number=1,
        tasks=[]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=plan_day_no_tasks) as mock_service:
        response = client.get("/plans/featured/day")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["day_number"] == 1
        assert data["tasks"] == []
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_with_optional_fields_none():
    subtask = SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.TEXT,
        content=None,
        display_order=None
    )
    
    task = TaskDTO(
        id=uuid4(),
        title=None,
        estimated_time=None,
        display_order=None,
        subtasks=[subtask]
    )
    
    plan_day = PlanDayDTO(
        id=uuid4(),
        day_number=10,
        tasks=[task]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=plan_day) as mock_service:
        response = client.get("/plans/featured/day")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        task_data = data["tasks"][0]
        assert task_data["title"] is None
        assert task_data["estimated_time"] is None
        assert task_data["display_order"] is None
        
        subtask_data = task_data["subtasks"][0]
        assert subtask_data["content"] is None
        assert subtask_data["display_order"] is None
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_no_featured_plans():
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", side_effect=HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No featured plans with days found"
    )) as mock_service:
        response = client.get("/plans/featured/day")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "No featured plans with days found"
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_database_error():
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", side_effect=HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database connection error"
    )) as mock_service:
        response = client.get("/plans/featured/day")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_service_exception():
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", side_effect=Exception("Unexpected error")) as mock_service:
        with pytest.raises(Exception):
            client.get("/plans/featured/day")
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_with_different_content_types():
    subtask_text = SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.TEXT,
        content="Read the instructions",
        display_order=1
    )
    
    subtask_video = SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.VIDEO,
        content="https://video.url/tutorial",
        display_order=2
    )
    
    subtask_audio = SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.AUDIO,
        content="https://audio.url/meditation",
        display_order=3
    )
    
    subtask_image = SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.IMAGE,
        content="https://image.url/diagram",
        display_order=4
    )
    
    task = TaskDTO(
        id=uuid4(),
        title="Multimedia Practice",
        estimated_time=45,
        display_order=1,
        subtasks=[subtask_text, subtask_video, subtask_audio, subtask_image]
    )
    
    plan_day = PlanDayDTO(
        id=uuid4(),
        day_number=20,
        tasks=[task]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=plan_day) as mock_service:
        response = client.get("/plans/featured/day")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        subtasks = data["tasks"][0]["subtasks"]
        assert len(subtasks) == 4
        assert subtasks[0]["content_type"] == ContentType.TEXT.value
        assert subtasks[1]["content_type"] == ContentType.VIDEO.value
        assert subtasks[2]["content_type"] == ContentType.AUDIO.value
        assert subtasks[3]["content_type"] == ContentType.IMAGE.value
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_with_large_day_number():
    plan_day = PlanDayDTO(
        id=uuid4(),
        day_number=365, 
        tasks=[]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=plan_day) as mock_service:
        response = client.get("/plans/featured/day")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["day_number"] == 365
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_with_many_subtasks():
    subtasks = [
        SubTaskDTO(
            id=uuid4(),
            content_type=ContentType.TEXT,
            content=f"Subtask {i}",
            display_order=i
        )
        for i in range(1, 21)    
    ]
    
    task = TaskDTO(
        id=uuid4(),
        title="Comprehensive Practice",
        estimated_time=120,
        display_order=1,
        subtasks=subtasks
    )
    
    plan_day = PlanDayDTO(
        id=uuid4(),
        day_number=50,
        tasks=[task]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=plan_day) as mock_service:
        response = client.get("/plans/featured/day")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["tasks"][0]["subtasks"]) == 20
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_multiple_calls_same_result():
    plan_day = PlanDayDTO(
        id=uuid4(),
        day_number=5,
        tasks=[]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=plan_day) as mock_service:
        response1 = client.get("/plans/featured/day")
        response2 = client.get("/plans/featured/day")
        response3 = client.get("/plans/featured/day")
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response3.status_code == status.HTTP_200_OK
        
        assert mock_service.call_count == 3
        
        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()
        
        assert data1["day_number"] == data2["day_number"] == data3["day_number"] == 5
