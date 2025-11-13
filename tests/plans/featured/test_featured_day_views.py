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
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=sample_plan_day_dto) as mock_service:
        response = client.get("/plans/featured/day?language=en")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "id" in data
        assert "day_number" in data
        assert "tasks" in data
        
        mock_service.assert_called_once_with(language="en")
        
        assert data["day_number"] == sample_plan_day_dto.day_number
        assert len(data["tasks"]) == len(sample_plan_day_dto.tasks)
        
        task = data["tasks"][0]
        assert "id" in task
        assert "title" in task
        assert "estimated_time" in task
        assert "display_order" in task
        assert "subtasks" in task
        
        subtask = task["subtasks"][0]
        assert "id" in subtask
        assert "content_type" in subtask
        assert "content" in subtask
        assert "display_order" in subtask
        assert subtask["content"] == "Practice deep breathing for 5 minutes"
        assert subtask["display_order"] == 1
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_with_custom_language(sample_plan_day_dto):
    """Test retrieval of featured day with custom language parameter."""
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=sample_plan_day_dto) as mock_service:
        response = client.get("/plans/featured/day?language=bo")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        mock_service.assert_called_once_with(language="bo")
        
        assert data["day_number"] == sample_plan_day_dto.day_number
        assert len(data["tasks"]) == len(sample_plan_day_dto.tasks)
        
        task = data["tasks"][0]
        assert "id" in task
        assert "title" in task
        assert "estimated_time" in task
        assert "display_order" in task
        assert "subtasks" in task
        
        subtask = task["subtasks"][0]
        assert "id" in subtask
        assert "content_type" in subtask
        assert "content" in subtask
        assert "display_order" in subtask
        assert subtask["content"] == "Practice deep breathing for 5 minutes"
        assert subtask["display_order"] == 1
        
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_featured_day_with_multiple_tasks(sample_plan_day_with_multiple_tasks):
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=sample_plan_day_with_multiple_tasks) as mock_service:
        response = client.get("/plans/featured/day?language=en")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        mock_service.assert_called_once_with(language="en")
        
        assert data["day_number"] == sample_plan_day_with_multiple_tasks.day_number
        assert len(data["tasks"]) == len(sample_plan_day_with_multiple_tasks.tasks)
        
        task1 = data["tasks"][0]
        assert "id" in task1
        assert "title" in task1
        assert "estimated_time" in task1
        assert "display_order" in task1
        assert "subtasks" in task1
        
        subtask1 = task1["subtasks"][0]
        assert "id" in subtask1
        assert "content_type" in subtask1
        assert "content" in subtask1
        assert "display_order" in subtask1
        assert subtask1["content_type"] == ContentType.TEXT.value
        assert subtask1["content"] == "Read introduction"
        assert subtask1["display_order"] == 1
        
        subtask2 = task1["subtasks"][1]
        assert "id" in subtask2
        assert "content_type" in subtask2
        assert "content" in subtask2
        assert "display_order" in subtask2
        assert subtask2["content_type"] == ContentType.VIDEO.value
        assert subtask2["content"] == "https://video.url/meditation-guide"
        assert subtask2["display_order"] == 2
        
        task2 = data["tasks"][1]
        assert "id" in task2
        assert "title" in task2
        assert "estimated_time" in task2
        assert "display_order" in task2
        assert "subtasks" in task2
        assert len(task2["subtasks"]) == 0


@pytest.mark.asyncio
async def test_get_featured_day_with_empty_tasks():
    empty_day = PlanDayDTO(
        id=uuid4(),
        day_number=1,
        tasks=[]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=empty_day) as mock_service:
        response = client.get("/plans/featured/day?language=en")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        mock_service.assert_called_once_with(language="en")
        
        assert data["day_number"] == empty_day.day_number
        assert data["tasks"] == []


@pytest.mark.asyncio
async def test_get_featured_day_with_optional_fields_none():
    subtask_with_none = SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.TEXT,
        content="Basic content",
        display_order=1
    )
    
    task_with_none = TaskDTO(
        id=uuid4(),
        title=None,
        estimated_time=None,
        display_order=1,
        subtasks=[subtask_with_none]
    )
    
    day_with_none = PlanDayDTO(
        id=uuid4(),
        day_number=10,
        tasks=[task_with_none]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=day_with_none) as mock_service:
        response = client.get("/plans/featured/day?language=en")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        mock_service.assert_called_once_with(language="en")
        
        task_data = data["tasks"][0]
        assert task_data["title"] is None
        assert task_data["estimated_time"] is None
        assert task_data["display_order"] == 1
        assert len(task_data["subtasks"]) == 1
        
        subtask_data = task_data["subtasks"][0]
        assert subtask_data["content"] == "Basic content"
        assert subtask_data["display_order"] == 1


@pytest.mark.asyncio
async def test_get_featured_day_no_featured_plans():
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", side_effect=HTTPException(status_code=404, detail="No featured plans with days found")) as mock_service:
        response = client.get("/plans/featured/day?language=en")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "No featured plans with days found"
        
        mock_service.assert_called_once_with(language="en")


@pytest.mark.asyncio
async def test_get_featured_day_database_error():
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", side_effect=HTTPException(status_code=500, detail="Database connection error")) as mock_service:
        response = client.get("/plans/featured/day?language=en")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Database connection error"
        
        mock_service.assert_called_once_with(language="en")


@pytest.mark.asyncio
async def test_get_featured_day_service_exception():
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", side_effect=Exception("Unexpected error")) as mock_service:
        with pytest.raises(Exception, match="Unexpected error"):
            client.get("/plans/featured/day?language=en")
        
        mock_service.assert_called_once_with(language="en")


@pytest.mark.asyncio
async def test_get_featured_day_with_different_content_types():
    subtask_text = SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.TEXT,
        content="Read this text",
        display_order=1
    )
    
    subtask_video = SubTaskDTO(
        id=uuid4(),
        content_type=ContentType.VIDEO,
        content="https://video.url/lesson",
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
        content="images/guide.jpg",
        display_order=4
    )
    
    task = TaskDTO(
        id=uuid4(),
        title="Mixed Content Task",
        estimated_time=45,
        display_order=1,
        subtasks=[subtask_text, subtask_video, subtask_audio, subtask_image]
    )
    
    day = PlanDayDTO(
        id=uuid4(),
        day_number=20,
        tasks=[task]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=day) as mock_service:
        response = client.get("/plans/featured/day?language=en")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        mock_service.assert_called_once_with(language="en")
        
        subtasks = data["tasks"][0]["subtasks"]
        assert len(subtasks) == 4
        assert subtasks[0]["content_type"] == ContentType.TEXT.value
        assert subtasks[1]["content_type"] == ContentType.VIDEO.value
        assert subtasks[2]["content_type"] == "AUDIO"
        assert subtasks[3]["content_type"] == "IMAGE"


@pytest.mark.asyncio
async def test_get_featured_day_with_large_day_number():
    day = PlanDayDTO(
        id=uuid4(),
        day_number=365,
        tasks=[]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=day) as mock_service:
        response = client.get("/plans/featured/day?language=en")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        mock_service.assert_called_once_with(language="en")
        
        assert data["day_number"] == 365


@pytest.mark.asyncio
async def test_get_featured_day_with_many_subtasks():
    subtasks = [
        SubTaskDTO(
            id=uuid4(),
            content_type=ContentType.TEXT,
            content=f"Step {i+1}",
            display_order=i+1
        )
        for i in range(20)
    ]
    
    task = TaskDTO(
        id=uuid4(),
        title="Complex Task",
        estimated_time=120,
        display_order=1,
        subtasks=subtasks
    )
    
    day = PlanDayDTO(
        id=uuid4(),
        day_number=50,
        tasks=[task]
    )
    
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=day) as mock_service:
        response = client.get("/plans/featured/day?language=en")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        mock_service.assert_called_once_with(language="en")
        
        assert len(data["tasks"][0]["subtasks"]) == 20
        assert data["tasks"][0]["subtasks"][0]["content"] == "Step 1"
        assert data["tasks"][0]["subtasks"][19]["content"] == "Step 20"


@pytest.mark.asyncio
async def test_get_featured_day_multiple_calls_same_result(sample_plan_day_dto):
    """Test that multiple calls to the endpoint return consistent results (caching behavior)."""
    with patch("pecha_api.plans.featured.featured_day_views.get_featured_day_service", return_value=sample_plan_day_dto) as mock_service:
        response1 = client.get("/plans/featured/day?language=en")
        response2 = client.get("/plans/featured/day?language=en")
        response3 = client.get("/plans/featured/day?language=en")
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response3.status_code == status.HTTP_200_OK
        
        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()
        
        assert data1 == data2 == data3
        
        assert mock_service.call_count == 3
        for call in mock_service.call_args_list:
            assert call.kwargs == {"language": "en"}
