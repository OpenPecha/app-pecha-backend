from .segments_models import Segment
from .segments_response_models import CreateSegmentRequest
from typing import List

async def create_segment(create_segment_request: CreateSegmentRequest) -> List[Segment]:
    new_segment_list = [
        Segment(
            text_id=create_segment_request.text_id,
            content=segment.content,
            mapping=segment.mapping
        )
        for segment in create_segment_request.segments
    ]
    # Store the insert result but don't return it directly
    insert_segments = await Segment.insert_many(new_segment_list)
    
    return new_segment_list