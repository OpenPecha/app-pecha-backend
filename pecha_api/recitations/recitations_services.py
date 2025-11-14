
from pecha_api.texts.texts_models import Text
from pecha_api.texts.texts_enums import TextType
from typing import List, Dict, Union
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

from pecha_api.collections.collections_repository import get_all_collections_by_parent, get_collection_id_by_slug
from pecha_api.texts.texts_service import get_root_text_by_collection_id



async def get_list_of_recitations_service(language: str) -> RecitationsResponse:
    collection_id = await get_collection_id_by_slug(slug="Liturgy")
    if collection_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.COLLECTION_NOT_FOUND)
    collections = await get_all_collections_by_parent(parent_id=collection_id)
    list_of_collections = [str(collection.id) for collection in collections]
    list_of_texts = []
    for collection_id in list_of_collections:
        text_id, text_title = await get_root_text_by_collection_id(collection_id=collection_id, language=language)
        if text_id is not None and text_title is not None:
            list_of_texts.append((text_id, text_title))

    recitations_dto = [RecitationDTO(title=text_title, text_id=text_id) for text_id, text_title in list_of_texts]
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
        # recitation has only one section
        section = table_of_content.sections[0]
        text = await get_text_details_by_text_id(text_id=table_of_content.text_id)
        for segment in section.segments:
            recitation_segment = {}
            
            segment_details = await get_segment_by_id(segment_id=segment.segment_id)
            mapped_segments = await get_related_mapped_segments(parent_segment_id=segment.segment_id)
            # filter the segments by type and language
            translations = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments=mapped_segments, type="version")
            transliterations = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments=mapped_segments, type="version")
            adaptations = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments=mapped_segments, type="adaptation")
            
            
            # get other related segments to this text segment
            for key, items, langs in [
                ("recitation", translations, recitation_details_request.recitation),
                ("translations", translations, recitation_details_request.translations),
                ("transliterations", transliterations, recitation_details_request.transliterations),
                ("adaptations", adaptations, recitation_details_request.adaptations),
            ]:
                recitation_segment[key] = _filter_by_type_and_language(key=key,items=items, languages=langs)

            # #get text toc segment
            # recitation_segment["translations"][text.language] = Segment(
            #     id=segment.segment_id,
            #     content=segment_details.content
            # )

            recitation_segment = RecitationSegment(**recitation_segment)
            segments.append(recitation_segment)
    return segments

def _filter_by_type_and_language(
    key:str,
    items: List[Union[SegmentTranslation, SegmentTransliteration, SegmentAdaptation]],
    languages: List[str]
) -> Dict[str, Segment]:
    return {
        item.language: Segment(
            id=item.segment_id,
            content=SegmentUtils.apply_bophono(segmentContent=item.content) if key == "transliterations" and item.language == "bo" else item.content
        )
        for item in items
        if item.language in languages
    }