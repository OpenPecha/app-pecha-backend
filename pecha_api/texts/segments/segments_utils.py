class SegmentUtils:
    
    @staticmethod
    async def get_count_of_each_commentary_and_version(segments: List[Segment]) -> Dict[str, int]:
        count = {
            "commentary": 0,
            "version": 0
        }
        for segment in segments:
            text_detail = await get_text_detail_by_id(segment.text_id)
            if text_detail.type == "commentary":
                count["commentary"] += 1
            elif text_detail.type == "version":
                count["version"] += 1
        return count
