from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from uuid import uuid4
from pecha_api.app import api

from pecha_api.texts.segments.segments_response_models import CreateSegmentRequest, CreateSegment, \
    SegmentTranslationsResponse, SegmentTranslation
from pecha_api.error_contants import ErrorConstants
from pecha_api.texts.segments.segments_response_models import ParentSegment

client = TestClient(api)

@patch("pecha_api.texts.segments.segments_views.get_translations_by_segment_id")
def test_get_translations_success(mock_get_translations):
    # Mock data
    segment_id = str(uuid4())
    mock_response = SegmentTranslationsResponse(
        parent_segment=ParentSegment(
            segment_id=segment_id,
            content="Test segment content"
        ),
        translations=[
            SegmentTranslation(
                segment_id="segment_id_1",
                text_id="text1",
                title='title',
                source='source',
                language='en',
                content="Translation 1"
            ),
            SegmentTranslation(
                segment_id="segment_id_2",
                text_id="text2",
                title='title2',
                source='source2',
                language='bo',
                content="Translation 2"
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
    assert data["parent_segment"]["segment_id"] == segment_id
    assert data["parent_segment"]["content"] == "Test segment content"
    assert len(data["translations"]) == 2
    
    # Verify first translation
    assert data["translations"][0]["text_id"] == "text1"
    assert data["translations"][0]["title"] == "title"
    assert data["translations"][0]["source"] == "source"
    assert data["translations"][0]["language"] == "en"
    assert data["translations"][0]["content"] == "Translation 1"
    
    # Verify second translation
    assert data["translations"][1]["text_id"] == "text2"
    assert data["translations"][1]["language"] == "bo"

@patch("pecha_api.texts.segments.segments_views.get_translations_by_segment_id")
def test_get_translations_with_pagination(mock_get_translations):
    segment_id = str(uuid4())
    mock_response = SegmentTranslationsResponse(
        parent_segment=ParentSegment(
            segment_id=segment_id,
            segment_number=1,
            content="Test segment content"
        ),
        translations=[
            SegmentTranslation(
                segment_id=f"segment_id_{i}",
                text_id=f"text{i}",
                title=f"title{i}",
                source=f"source{i}",
                language='en',
                content=f"Translation {i}"
            ) for i in range(5)
        ]
    )
    
    mock_get_translations.return_value = mock_response
    response = client.get(f"/api/v1/segments/{segment_id}/translations?skip=2&limit=3")
    
    assert response.status_code == status.HTTP_200_OK
    mock_get_translations.assert_called_with(segment_id=segment_id)

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
    segment_id = str(uuid4())
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
        "segments": [
            {
            "id": segment_id,
            "text_id": segment_request.text_id,
            "content": segment_request.segments[0].content,
            "mapping": segment_request.segments[0].mapping
            }
        ]

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
    
    # Verify segment
    assert data['segments'][0]["text_id"] == segment_request.text_id
    assert data['segments'][0]["content"] == segment_request.segments[0].content
    assert data['segments'][0]["id"] == segment_id

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