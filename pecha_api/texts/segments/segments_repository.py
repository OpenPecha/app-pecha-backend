from __future__ import annotations

from uuid import UUID

from pecha_api.constants import Constants
from .segments_models import Segment
from .segments_response_models import CreateSegmentRequest, SegmentDTO
import logging
from beanie.exceptions import CollectionWasNotInitialized
from typing import List, Dict


async def get_segment_by_id(segment_id: str) -> SegmentDTO | None:
    try:
        segment = await Segment.get_segment_by_id(segment_id=segment_id)
        return segment
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return None

async def get_segment_details_by_id(segment_id: str):
    return await Segment.get_segment_details(segment_id=segment_id)

async def check_segment_exists(segment_id: UUID) -> bool:
    try:
        is_segment_exists = await Segment.check_exists(segment_id=segment_id)
        return is_segment_exists
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return False


async def check_all_segment_exists(segment_ids: List[UUID]) -> bool:
    try:
        is_segment_exists = await Segment.exists_all(segment_ids=segment_ids, batch_size=Constants.QUERY_BATCH_SIZE)
        return is_segment_exists
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return False


async def get_segments_by_ids(segment_ids: List[str]) -> Dict[str, SegmentDTO]:
    try:
        if not segment_ids:
            return {}
        list_of_segments_detail = await Segment.get_segments(segment_ids=segment_ids)
        return {str(segment.id): SegmentDTO(
            id=str(segment.id),
            text_id=segment.text_id,
            content=segment.content,
            mapping=segment.mapping
        ) for segment in list_of_segments_detail}
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return {}


async def create_segment(create_segment_request: CreateSegmentRequest) -> List[Segment]:
    new_segment_list = [
        Segment(
            text_id=create_segment_request.text_id,
            content=segment.content,
            mapping=segment.mapping,
            type=segment.type
        )
        for segment in create_segment_request.segments
    ]
    # Store the insert result but don't return it directly
    await Segment.insert_many(new_segment_list)

    return new_segment_list

async def get_related_mapped_segments(parent_segment_id: str) -> List[SegmentDTO]:
    try:
        segments = await Segment.get_related_mapped_segments(parent_segment_id=parent_segment_id)
        return segments
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return []
