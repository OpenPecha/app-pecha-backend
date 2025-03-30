import uuid
from typing import List, Optional

from ..segments.segments_models import Mapping, Segment


async def update_mapping(segment_id: uuid.UUID, text_id: str, mappings: List[Mapping]) -> Optional[Segment]:
    result = await Segment.get_segment_by_id_and_text_id(segment_id=segment_id, text_id=text_id)
    if result:
        result.mapping = mappings
        await result.save()
        return result
    return None