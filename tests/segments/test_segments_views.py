from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from uuid import uuid4
from pecha_api.app import api

from pecha_api.texts.texts_response_models import TextSegment, Translation
from pecha_api.texts.segments.segments_response_models import CreateSegmentRequest, CreateSegment, SegmentTranslationsResponse
from pecha_api.error_contants import ErrorConstants

client = TestClient(api)

@patch("pecha_api.texts.segments.segments_views.get_translations_by_segment_id")
def test_get_translations_success(mock_get_translations):
    # Mock data
    segment_id = str(uuid4())
    mock_response = SegmentTranslationsResponse(
        segment=TextSegment(
            segment_id=segment_id,
            segment_number=1,
            content="Test segment content"
        ),
        translations=[
            Translation(
                text_id="text1",
                language='en',
                content="Translation 1"
            )
        ]
    )
    
    # Mock the service function
    mock_get_translations.return_value = mock_response
    # Make request
    response = client.get(f"/api/v1/segments/{segment_id}/translations")
    
    # Assert response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["segment"]["segment_id"] == segment_id
    assert data["segment"]["content"] == "Test segment content"
    assert len(data["translations"]) == 1
    assert data["translations"][0]["text_id"] == "text1"

@patch("pecha_api.texts.segments.segments_views.get_translations_by_segment_id")
def test_get_translations_with_pagination(mock_get_translations):
    segment_id = str(uuid4())
    mock_response = SegmentTranslationsResponse(
        segment=TextSegment(
            segment_id=segment_id,
            segment_number=1,
            content="Test segment content"
        ),
        translations=[
            Translation(text_id=f"text{i}", language='en', content=f"Translation {i}")
            for i in range(5)
        ]
    )
    
    mock_get_translations.return_value = mock_response
    response = client.get(f"/api/v1/segments/{segment_id}/translations?skip=2&limit=3")
    
    assert response.status_code == status.HTTP_200_OK
    mock_get_translations.assert_called_with(segment_id=segment_id, skip=2, limit=3)

@patch("pecha_api.texts.segments.segments_views.get_translations_by_segment_id")
def test_get_translations_not_found(mock_get_translations):
    segment_id = str(uuid4())
    mock_get_translations.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE
    )
    
    response = client.get(f"/api/v1/segments/{segment_id}/translations")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE

@patch("pecha_api.texts.segments.segments_views.create_new_segment")
def test_create_segment_success(mock_create_segment):
    # Mock data
    segment_request = CreateSegmentRequest(
        text_id="text123",
        segments=[
            CreateSegment(
                content="New segment content",
                mapping=[]
            )
        ]
    )
    mock_response = {
        "id": str(uuid4()),
        "text_id": segment_request.text_id,
        "content": segment_request.segments[0].content,
        "mapping": []
    }
    mock_create_segment.return_value = mock_response
    
    # Make request with auth token
    response = client.post(
        "/api/v1/segments",
        json=segment_request.model_dump(),
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["text_id"] == segment_request.text_id
    assert data["content"] == segment_request.segments[0].content
    assert "id" in data
    assert isinstance(data["mapping"], list)

def test_create_segment_unauthorized():
    segment_request = CreateSegmentRequest(
        text_id="text123",
        segments=[
            CreateSegment(
                content="New segment content",
                mapping=[]
            )
        ]
    )
    
    # Make request without auth token
    response = client.post(
        "/api/v1/segments",
        json=segment_request.model_dump()
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN