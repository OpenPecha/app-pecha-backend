from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
import pytest
from pecha_api.texts.segments.segments_service import create_new_segment, validate_segment_exists, validate_segments_exists, \
    get_translations_by_segment_id
from pecha_api.texts.segments.segments_response_models import CreateSegmentRequest, SegmentResponse, CreateSegment, \
    ParentSegment, SegmentTranslationsResponse, SegmentTranslation
from pecha_api.texts.segments.segments_models import Segment
from pecha_api.error_contants import ErrorConstants

@pytest.mark.asyncio
async def test_validate_segment_exists_true():
    """
    Test case for the validate_segment_exists function from the segments_service file
    """
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"

    with patch('pecha_api.texts.segments.segments_service.check_segment_exists', return_value=True):
        response = await validate_segment_exists(segment_id=segment_id)
        assert response is True

@pytest.mark.asyncio
async def test_validate_segment_exits_false():
    """
    Test case for the validate_segment_exists function from the segments_service file
    """
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"

    with patch('pecha_api.texts.segments.segments_service.check_segment_exists', return_value=False):
        with pytest.raises(HTTPException) as excinfo:
            await validate_segment_exists(segment_id=segment_id)
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_validate_segments_exists_true():
    """
    Test case for the validate_segments_exists function from the segments_service file
    """
    segment_ids = ["efb26a06-f373-450b-ba57-e7a8d4dd5b64", "efb26a06-f373-450b-ba57-e7a8d4dd5b64"]

    with patch('pecha_api.texts.segments.segments_service.check_all_segment_exists', return_value=True):
        response = await validate_segments_exists(segment_ids=segment_ids)
        assert response is True

@pytest.mark.asyncio
async def test_validate_segments_exits_false():
    """
    Test case for the validate_segments_exists function from the segments_service file
    """
    segment_ids = ["efb26a06-f373-450b-ba57-e7a8d4dd5b64", "efb26a06-f373-450b-ba57-e7a8d4dd5b64"]

    with patch('pecha_api.texts.segments.segments_service.check_all_segment_exists', return_value=False):
        with pytest.raises(HTTPException) as excinfo:
            await validate_segments_exists(segment_ids=segment_ids)
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_get_translations_by_segment_id():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    parent_segment = ParentSegment(
            segment_id=segment_id,
            segment_number=1,
            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།"
        )
    translations = [
        SegmentTranslation(
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            title = f"Title {i}",
            source = f"source {i}",
            language = "en",
            content="To the buddhas: Vipaśyin,<br> Śikhin, Viśvabhū,<br>   Krakucchanda, Kanakamuni,<br> and Kāśyapa,<br>   And Śākyamuni—Gautama,<br> deity of all deities,   <br>To the seven warrior-like buddhas, I pay homage!",
        )
        for i in range(1, 4)
    ]
    with patch("pecha_api.texts.segments.segments_service.get_segment_by_id", new_callable=AsyncMock) as mock_segment, \
        patch("pecha_api.texts.segments.segments_service.get_translations", new_callable=AsyncMock) as mock_translations:
        mock_segment.return_value = parent_segment
        mock_translations.return_value = translations

        response = await get_translations_by_segment_id(segment_id=segment_id)
        assert response == SegmentTranslationsResponse(
            parent_segment=parent_segment,
            translations=translations
        )

@pytest.mark.asyncio
async def test_get_translations_by_segment_id_segment_not_found():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"

    with patch("pecha_api.texts.segments.segments_service.get_segment_by_id", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as excinfo:
            await get_translations_by_segment_id(segment_id=segment_id)
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE

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
    
@pytest.mark.asyncio
async def test_create_new_segment_non_admin():
    """
    Test case for the create_new_segment function from the segments_service file when non admin tries to create segment
    """
    create_segment_request = CreateSegmentRequest(
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        segments=[
            CreateSegment(content="content", mapping=[])
        ]
    )

    with patch('pecha_api.texts.segments.segments_service.verify_admin_access', return_value=False):
        with pytest.raises(HTTPException) as excinfo:
            await create_new_segment(
                create_segment_request=create_segment_request,
                token="non-admin"
            )
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == ErrorConstants.ADMIN_ERROR_MESSAGE