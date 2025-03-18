from unittest.mock import AsyncMock, patch

import pytest
from pecha_api.texts.segments.segments_service import create_new_segment
from pecha_api.texts.segments.segments_response_models import CreateSegmentRequest, SegmentResponse, CreateSegment
from pecha_api.texts.segments.segments_models import Segment

@pytest.mark.asyncio
async def test_create_new_segment():
    with patch('pecha_api.texts.segments.segments_service.verify_admin_access', return_value=True), \
        patch('pecha_api.texts.segments.segments_service.create_segment', new_callable=AsyncMock) as mock_create_segment:
        mock_create_segment.return_value = AsyncMock(id="efb26a06-f373-450b-ba57-e7a8d4dd5b64", text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64", content="content", mapping=[])
        response = await create_new_segment(
            create_segment_request=CreateSegmentRequest(
                text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
                segments=[CreateSegment(content="content", mapping=[])]
            ),
            token="admin"
        )
        print("HERE -> ", response)
        assert response == [SegmentResponse(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            content="content",
            mapping=[]
        )]