from typing import Any
import uuid

from uploader_app.segments.segment_service import SegmentService
from uploader_app.table_of_contents.toc_repository import post_toc
from uploader_app.table_of_contents.toc_upload_log import log_uploaded_toc, is_toc_uploaded
from uploader_app.config import TEXT_UPLOAD_LOG_FILE


class TocService:
    def __init__(self):
        self.segment_service = SegmentService()

    async def upload_toc(self):
        text_pairs = await self.segment_service.get_pecha_text_ids_from_csv()

        for pecha_text_id, text_id in text_pairs:
            # Check if TOC already uploaded for this pecha_text_id
            if is_toc_uploaded(pecha_text_id):
                print(f"TOC already uploaded for pecha_text_id: {pecha_text_id}, skipping...")
                continue
            
            instance = await self.segment_service.get_segments_annotation_by_pecha_text_id(pecha_text_id)
            annotation_ids = self.segment_service.get_annotation_ids(instance)
            annotation_sengments = await self.segment_service.get_segments_by_id_list(annotation_ids[0])
            ordered_segments = await self.order_segments_by_annotation_span(annotation_sengments)
            create_toc_payload = await self.create_toc_payload(ordered_segments, text_id)
            
            
            response = await post_toc(create_toc_payload)
            print("toc uploaded successfully>>>>>>>>>>>>>>>>>",response["_id"])
            
        
            # Log the uploaded TOC
            log_uploaded_toc(
                pecha_text_id=pecha_text_id,
                id=response.get("_id"),
                text_id=response.get("text_id")
            )
        
    async def order_segments_by_annotation_span(self, annotation_sengments: dict[str, Any]):

        segments_data = annotation_sengments.get("data", [])
        sorted_segments = sorted(segments_data, key=lambda x: x["span"]["start"])
        result = [
            {"segment_id": segment["id"], "segment_number": idx + 1}
            for idx, segment in enumerate(sorted_segments)
        ]
        return result

    async def create_toc_payload(self, ordered_segments: list[dict[str, Any]], text_id: str):
        section_id = str(uuid.uuid4())
        payload = {
            "text_id": text_id,
            "type": "text",
            "sections": [
                {
                    "id": section_id,
                    "title": "1",
                    "section_number": 1,
                    "segments": ordered_segments
                }
            ]
        }
        return payload

    async def get_toc_from_database(self):
        pass