from pecha_api.texts.texts_models import Text
from pecha_api.texts.texts_enums import TextType
from typing import List, Dict
from fastapi import HTTPException
from starlette import status
from uuid import UUID

from pecha_api.error_contants import ErrorConstants

# Texts
from pecha_api.texts.texts_utils import TextUtils
from pecha_api.texts.texts_response_models import TextDTO, TableOfContent
from pecha_api.texts.texts_repository import get_texts_by_group_id, get_contents_by_id

# Segments
from pecha_api.texts.segments.segments_service import get_segment_by_id, get_related_mapped_segments
from pecha_api.texts.segments.segments_utils import SegmentUtils
from pecha_api.texts.segments.segments_response_models import SegmentTranslation, SegmentTransliteration, SegmentAdaptation

# Recitations
from pecha_api.recitations.recitations_response_models import (
    RecitationDTO, 
    RecitationsResponse, 
    RecitationDetailsRequest, 
    RecitationDetailsResponse,
    Segment,
    RecitationSegment
)

async def get_list_of_recitations_service() -> RecitationsResponse:
    recitations = await Text.get_list_of_recitations(type=TextType.RECITATION)
    recitations_dto = [RecitationDTO(title=recitation.title, text_id=recitation.id) for recitation in recitations]
    return RecitationsResponse(recitations=recitations_dto)

async def get_recitation_details_service(text_id: str, recitation_details_request: RecitationDetailsRequest) -> RecitationDetailsResponse:
    is_valid_text: bool = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
  
    text_detail: TextDTO = await get_text_details_by_text_id(text_id=text_id)

    group_id: str = text_detail.group_id
    texts: List[TextDTO] = await get_texts_by_group_id(group_id=group_id, skip=0, limit=10)
    
    filtered_text_on_root_and_version = TextUtils.filter_text_on_root_and_version(texts=texts, language=recitation_details_request.language)
    root_text: TextDTO = filtered_text_on_root_and_version["root_text"]
    if root_text is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    table_of_contents: List[TableOfContent] = await get_contents_by_id(text_id=root_text.id)
    segments = await _segments_mapping_by_toc(table_of_contents=table_of_contents, recitation_details_request=recitation_details_request)

    recitation_details_response = RecitationDetailsResponse(
        text_id=UUID(text_detail.id),
        title=text_detail.title,
        segments=segments   
    )
   
    return recitation_details_response

async def get_text_details_by_text_id(text_id: str) -> TextDTO:
    return await TextUtils.get_text_detail_by_id(text_id=text_id)


async def _segments_mapping_by_toc(table_of_contents: List[TableOfContent], recitation_details_request: RecitationDetailsRequest) -> List[Segment]:
    segments = []
    for table_of_content in table_of_contents:
        print("table_of_content>>>>>>>>>>>>>>>>>>>>>>>>>>>>",table_of_content.text_id)
        # recitation has only one section
        section = table_of_content.sections[0]
        for segment in section.segments:
            recitation_segment = {}
            text = await get_text_details_by_text_id(text_id=table_of_content.text_id)
            
            segment_details = await get_segment_by_id(segment_id=segment.segment_id)
            mapped_segments = await get_related_mapped_segments(parent_segment_id=segment_details.id)
            # filter the segments by type and language
            translations = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments=mapped_segments, type="version")
            transliterations = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments=mapped_segments, type="transliteration")
            adaptations = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments=mapped_segments, type="adaptation")

            # filter the segments by language
            if text.language in recitation_details_request.recitation:
                recitation_segment["recitation"] = {text.language: Segment(
                        id=segment.segment_id,
                        content=segment_details.content,
                        segment_number=segment.segment_number
                    )}

            recitation_segment["translations"] = _filter_translation_by_language(translations=translations, languages=recitation_details_request.translations)
            recitation_segment["transliterations"] = _filter_transliteration_by_language(transliterations=transliterations, languages=recitation_details_request.transliterations)
            recitation_segment["adaptations"] = _filter_adaptation_by_language(adaptations=adaptations, languages=recitation_details_request.adaptations)
            recitation_segment = RecitationSegment(**recitation_segment)
            segments.append(recitation_segment)
    return segments


def _filter_translation_by_language(translations: List[SegmentTranslation], languages: List[str]) -> Dict[str, Segment]:
    return {translation.language: Segment(
        id=translation.segment_id,
        content=translation.content
    ) for translation in translations if translation.language in languages}

def _filter_transliteration_by_language(transliterations: List[SegmentTransliteration], languages: List[str]) -> Dict[str, Segment]:
    return {transliteration.language: Segment(
        id=transliteration.segment_id,
        content=transliteration.content
    ) for transliteration in transliterations if transliteration.language in languages}

def _filter_adaptation_by_language(adaptations: List[SegmentAdaptation], languages: List[str]) -> Dict[str, Segment]:
    return {adaptation.language: Segment(
        id=adaptation.segment_id,
        content=adaptation.content
    ) for adaptation in adaptations if adaptation.language in languages}