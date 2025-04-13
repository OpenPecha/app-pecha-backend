import uuid
from typing import List, Optional, Dict
from .mappings_response_models import TextMapping, MappingsModel
from ..segments.segments_models import Mapping, Segment 

async def update_mapping(segment_id: uuid.UUID, text_id: str, mappings: List[Mapping]) -> Optional[Segment]:
    result = await Segment.get_segment_by_id_and_text_id(segment_id=segment_id, text_id=text_id)
    if result:
        result.mapping = mappings
        await result.save()
        return result
    return None

async def update_mappings(text_mappings: List[TextMapping]) -> List[Segment]:
    """
    Update mappings for multiple segments and return the updated segments.
    
    Returns:
        List[Segment]: List of updated segments
    
    Raises:
        ValueError: If no valid segments found to update
    """
    # Convert text mappings to segment dictionary
    segment_dict : Dict[str, List[Mapping]] = get_segments_from_text_mapping(text_mappings=text_mappings)
    if not segment_dict:
        return []

    # Get all segments that need to be updated
    segment_ids: List[str] = list(segment_dict.keys())
    segments = await Segment.get_segments(segment_ids=segment_ids)
    if not segments:
        raise ValueError("No valid segments found to update")
        
    # Update segment mappings and save each segment
    updated_segments = []
    for segment in segments:
        if str(segment.id) in segment_dict:  # Convert UUID to string for comparison
            segment.mapping = segment_dict[str(segment.id)]
            await segment.save()
            updated_segments.append(segment)
            
    return updated_segments




def get_segments_from_text_mapping(text_mappings: List[TextMapping]) -> Dict[str, List[Mapping]]:
    """
    Convert text mappings to a dictionary of segment IDs and their mappings.
    Converts MappingsModel to Mapping objects for compatibility with Segment model.
    """
    segment_dict = {}
    for text_mapping in text_mappings:
        # Convert MappingsModel to Mapping objects
        mappings = [
            Mapping(text_id=m.parent_text_id, segments=m.segments)
            for m in text_mapping.mappings
        ]
        # Ensure segment_id is stored as string
        segment_dict[str(text_mapping.segment_id)] = mappings
    return segment_dict
