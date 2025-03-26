from unittest.mock import AsyncMock, patch

import pytest
from pecha_api.texts.segments.segments_service import create_new_segment
from pecha_api.texts.segments.segments_response_models import CreateSegmentRequest, SegmentResponse, CreateSegment
from pecha_api.texts.segments.segments_models import Segment

@pytest.mark.asyncio
async def test_create_new_segment():
    """
    Test case for the create_new_segment function from the segments_service file
    """
    create_segment_request = CreateSegmentRequest(
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        segments=[
            CreateSegment(content="content", mapping=[])
        ]
    )

    with patch('pecha_api.texts.segments.segments_service.verify_admin_access', return_value=True), \
        patch('pecha_api.texts.segments.segments_service.validate_text_exits', new_callable=AsyncMock, return_value=True), \
        patch('pecha_api.texts.segments.segments_service.create_segment', new_callable=AsyncMock) as mock_create_segment:
        mock_segment_list = [
            SegmentResponse(
                id="efb26a06-f373-450b-ba57-e7a8d4dd5b64", 
                text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64", 
                content="content", 
                mapping=[]
            )
        ]
        mock_create_segment.return_value = mock_segment_list
        
        response = await create_new_segment(
            create_segment_request=create_segment_request,
            token="admin"
        )
        assert response == [
            SegmentResponse(
                id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
                text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
                content="content",
                mapping=[]
            )
        ]