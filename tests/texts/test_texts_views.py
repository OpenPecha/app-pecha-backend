from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from pecha_api.app import api
from pecha_api.texts.texts_response_models import (
    CreateTextRequest,
    TableOfContentResponse,
    TextDetailsRequest,
    TextDTO,
    TextVersionResponse,
    TextVersion,
    DetailTableOfContentResponse,
    TableOfContent,
    Section
)

client = TestClient(api)

# Test data
MOCK_TEXT_DTO = TextDTO(
    id="123e4567-e89b-12d3-a456-426614174000",
    title="Test Text",
    language="bo",
    group_id="123e4567-e89b-12d3-a456-426614174000",
    type="VERSION",
    is_published=True,
    created_date="2025-01-01T00:00:00",
    updated_date="2025-01-01T00:00:00",
    published_date="2025-01-01T00:00:00",
    published_by="test_user",
    categories=[],
    views=0
)

# Create a simple section for the table of contents
mock_section = Section(
    id="123e4567-e89b-12d3-a456-426614174002",
    title="Chapter 1",
    section_number=1,
    parent_id=None,
    segments=[],
    sections=[],
    created_date="2025-01-01T00:00:00",
    updated_date="2025-01-01T00:00:00",
    published_date="2025-01-01T00:00:00"
)

# Create a table of content with the section
MOCK_TABLE_OF_CONTENT = TableOfContent(
    id="123e4567-e89b-12d3-a456-426614174001",
    text_id="123e4567-e89b-12d3-a456-426614174000",
    sections=[mock_section]
)



# Create response objects
# Create a proper DetailTableOfContentResponse
MOCK_TABLE_OF_CONTENT_RESPONSE = TableOfContentResponse(
    text_detail=MOCK_TEXT_DTO,
    contents=[MOCK_TABLE_OF_CONTENT]
)

# For testing details endpoint
MOCK_DETAIL_TABLE_OF_CONTENT_RESPONSE = DetailTableOfContentResponse(
    text_detail=MOCK_TEXT_DTO,
    mapping={"segment_id": "seg123", "section_id": "sec123"},
    content={
        "id": "content123",
        "text_id": "123e4567-e89b-12d3-a456-426614174000",
        "sections": []
    },
    skip=0,
    current_section=0,
    limit=10,
    total=1
)

# Create a TextVersion instance for the response
MOCK_TEXT_VERSION = TextVersion(
    id="123e4567-e89b-12d3-a456-426614174003",
    title="Test Text Version",
    parent_id=None,
    priority=1,
    language="bo",
    type="VERSION",
    group_id="123e4567-e89b-12d3-a456-426614174004",
    table_of_contents=[],
    is_published=True,
    created_date="2025-01-01T00:00:00",
    updated_date="2025-01-01T00:00:00",
    published_date="2025-01-01T00:00:00",
    published_by="test_user"
)

MOCK_TEXT_VERSION_RESPONSE = TextVersionResponse(
    text=MOCK_TEXT_DTO,
    versions=[MOCK_TEXT_VERSION]
)

# Mock authentication token
VALID_TOKEN = "valid_token_123"

@pytest.mark.asyncio
async def test_get_text_by_text_id(mocker):
    """Test GET /texts with text_id parameter"""
    # Mock the service function
    mock_get_text = mocker.patch(
        'pecha_api.texts.texts_views.get_text_by_text_id_or_term',
        new_callable=AsyncMock,
        return_value=MOCK_TEXT_DTO
    )
    
    # The text ID that will be used in the request
    test_text_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Make the request - using query parameter instead of path parameter
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get(f"/texts?text_id={test_text_id}&language=bo&skip=0&limit=10")
    
    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, dict)
    assert response_data["id"] == MOCK_TEXT_DTO.id
    assert response_data["title"] == MOCK_TEXT_DTO.title
    assert response_data["language"] == MOCK_TEXT_DTO.language
    mock_get_text.assert_called_once_with(
        text_id="123e4567-e89b-12d3-a456-426614174000",
        term_id=None,
        language="bo",
        skip=0,
        limit=10
    )

@pytest.mark.asyncio
async def test_get_text_by_term_id(mocker):
    """Test GET /texts with term_id parameter"""
    # Mock the service function
    mock_get_text = mocker.patch(
        'pecha_api.texts.texts_views.get_text_by_text_id_or_term',
        new_callable=AsyncMock,
        return_value=MOCK_TEXT_DTO
    )
    
    # The term ID that will be used in the request
    test_term_id = "123e4567-e89b-12d3-a456-426614174001"
    
    # Make the request
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get(f"/texts?term_id={test_term_id}&language=bo&skip=0&limit=10")
    
    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, dict)
    assert response_data["id"] == MOCK_TEXT_DTO.id
    assert response_data["title"] == MOCK_TEXT_DTO.title
    assert response_data["language"] == MOCK_TEXT_DTO.language
    # Remove the contents check as it's not part of the TextDTO model
    mock_get_text.assert_called_once_with(
        text_id=None,
        term_id=test_term_id,
        language="bo",
        skip=0,
        limit=10
    )

@pytest.mark.asyncio
async def test_create_text_success(mocker):
    """Test POST /texts with valid data"""
    # Mock the service function
    mock_create_text = mocker.patch(
        'pecha_api.texts.texts_views.create_new_text',
        new_callable=AsyncMock,
        return_value=MOCK_TEXT_DTO
    )
    
    # Test data - match the CreateTextRequest model
    # Note: The mock returns MOCK_TEXT_DTO which has title="Test Text"
    create_data = {
        "title": "Test Text",  # Match the mock data
        "language": "bo",
        "isPublished": True,
        "group_id": "123e4567-e89b-12d3-a456-426614174000",
        "type": "VERSION",
        "published_by": "test_user",
        "categories": []
    }
    
    # Make the request
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.post(
            "/texts",
            json=create_data,
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
    
    # Assertions - 201 Created is the correct status code for resource creation
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["title"] == create_data["title"]
    assert response_data["language"] == create_data["language"]
    assert response_data["type"] == create_data["type"]
    assert response_data["is_published"] == create_data["isPublished"]
    mock_create_text.assert_called_once()
    call_args = mock_create_text.call_args[1]
    assert call_args["token"] == VALID_TOKEN
    assert isinstance(call_args["create_text_request"], CreateTextRequest)

@pytest.mark.asyncio
async def test_get_versions_success(mocker):
    """Test GET /texts/{text_id}/versions"""
    # Mock the service function
    mock_get_versions = mocker.patch(
        'pecha_api.texts.texts_views.get_text_versions_by_group_id',
        new_callable=AsyncMock,
        return_value={
            "text": MOCK_TEXT_DTO,
            "versions": [MOCK_TEXT_VERSION.model_dump()]
        }
    )
    
    # The text ID that will be used in the request
    test_text_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Make the request
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get(f"/texts/{test_text_id}/versions?language=bo&skip=0&limit=10")
    
    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert "text" in response_data
    assert "versions" in response_data
    assert isinstance(response_data["versions"], list)
    if response_data["versions"]:  # Check only if versions list is not empty
        version = response_data["versions"][0]
        assert "id" in version
        assert "title" in version
        assert "language" in version
    mock_get_versions.assert_called_once_with(
        text_id=test_text_id,
        language="bo",
        skip=0,
        limit=10
    )

@pytest.mark.asyncio
async def test_get_contents_success(mocker):
    """Test GET /texts/{text_id}/contents"""
    # Mock the service function
    mock_get_contents = mocker.patch(
        'pecha_api.texts.texts_views.get_table_of_contents_by_text_id',
        new_callable=AsyncMock,
        return_value=MOCK_TABLE_OF_CONTENT_RESPONSE
    )
    
    # Make the request
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get("/texts/123e4567-e89b-12d3-a456-426614174000/contents")
    
    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert "text_detail" in response_data
    assert "contents" in response_data
    assert isinstance(response_data["contents"], list)
    assert len(response_data["contents"]) > 0
    mock_get_contents.assert_called_once_with(text_id="123e4567-e89b-12d3-a456-426614174000")

@pytest.mark.asyncio
async def test_get_contents_with_details_success(mocker):
    """Test POST /texts/{text_id}/details"""
    # Mock the service function
    mock_get_details = mocker.patch(
        'pecha_api.texts.texts_views.get_text_details_by_text_id',
        new_callable=AsyncMock,
        return_value=MOCK_DETAIL_TABLE_OF_CONTENT_RESPONSE
    )
    
    # Test data
    request_data = {
        "content_id": "123e4567-e89b-12d3-a456-426614174003",
        "version_id": "123e4567-e89b-12d3-a456-426614174004",
        "section_id": "123e4567-e89b-12d3-a456-426614174005",
        "segment_id": "123e4567-e89b-12d3-a456-426614174006"
    }
    
    # Make the request
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.post(
            "/texts/123e4567-e89b-12d3-a456-426614174000/details",
            json=request_data
        )
    
    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert "text_detail" in response_data
    assert "mapping" in response_data
    assert "content" in response_data
    assert "current_section" in response_data
    assert "limit" in response_data
    assert "total" in response_data
    
    # Verify the mock was called with the correct arguments
    mock_get_details.assert_called_once()
    call_args = mock_get_details.call_args[1]
    assert call_args["text_id"] == "123e4567-e89b-12d3-a456-426614174000"
    assert isinstance(call_args["text_details_request"], TextDetailsRequest)

@pytest.mark.asyncio
async def test_create_table_of_content_success(mocker):
    """Test POST /texts/table-of-content"""
    # Mock the service function
    mock_create_toc = mocker.patch(
        'pecha_api.texts.texts_views.create_table_of_content',
        new_callable=AsyncMock,
        return_value=MOCK_TABLE_OF_CONTENT
    )
    
    # Test data - match the TableOfContent model
    toc_data = {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "text_id": "123e4567-e89b-12d3-a456-426614174000",
        "sections": [
            {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "title": "Chapter 1",
                "section_number": 1,
                "parent_id": None,
                "segments": [],
                "sections": [],
                "created_date": "2025-01-01T00:00:00",
                "updated_date": "2025-01-01T00:00:00",
                "published_date": "2025-01-01T00:00:00",
                "published_by": "test_user"
            }
        ]
    }
    
    # Make the request
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.post(
            "/texts/table-of-content",
            json=toc_data,
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
    
    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert "id" in response_data
    assert "text_id" in response_data
    assert "sections" in response_data
    assert response_data["text_id"] == toc_data["text_id"]
    mock_create_toc.assert_called_once()
    call_args = mock_create_toc.call_args[1]
    assert call_args["token"] == VALID_TOKEN
    assert isinstance(call_args["table_of_content_request"], TableOfContent)

# Error case tests

@pytest.mark.asyncio
async def test_create_text_unauthorized():
    """Test POST /texts without authentication"""
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.post("/texts", json={"title": "Test"})
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_table_of_content_unauthorized():
    """Test POST /texts/table-of-content without authentication"""
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.post("/texts/table-of-content", json={"text_id": "123e4567-e89b-12d3-a456-426614174000"})
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_contents_not_found(mocker):
    """Test GET /texts/{text_id}/contents with non-existent text"""
    mocker.patch(
        'pecha_api.texts.texts_views.get_table_of_contents_by_text_id',
        side_effect=HTTPException(status_code=404, detail="Text not found")
    )
    
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get("/texts/non_existent_id/contents")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Text not found"
