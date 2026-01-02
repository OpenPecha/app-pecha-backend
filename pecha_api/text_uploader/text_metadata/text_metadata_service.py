from typing import Any, List
from uuid import uuid4 as uuid
import json

from pecha_api.text_uploader.text_uploader_response_model import TextUploadRequest
from pecha_api.text_uploader.text_metadata.text_metadata_model import CriticalInstanceResponse
from pecha_api.text_uploader.text_metadata.text_group_repository import (
    get_texts,
    get_text_groups,
    post_group,
    get_critical_instances,
    post_text,
    get_related_texts,
    get_text_instances,
    get_text_related_by_work,
    get_text_metadata,
    get_texts_by_category
)
from pecha_api.text_uploader.constants import TextType
from pecha_api.text_uploader.text_metadata.text_metadata_model import TextGroupPayload


class TextMetadataService:
    def __init__(self):
        self.version_group_id: str | None = None
        self.commentary_group_id: str | None = None
        self.text_ids: list[str] = []
        self.category: dict[str, str] = {}


    async def upload_text_metadata_service(self, text_upload_request: TextUploadRequest, token: str):
        text_id = text_upload_request.text_id
        text = await get_text_metadata(text_id)

        related_text_ids = []
        commentary_text_ids = []
        work_translation_group = {}

        text_related_by_work_response = await get_text_related_by_work(text_id)
        for key in text_related_by_work_response.keys():
            if text_related_by_work_response[key]["relation"] not in ['commentary', 'sibling_commentary']:
                work_translation_group[key] = text_related_by_work_response[key]["expression_ids"]
                expression_ids = text_related_by_work_response[key]["expression_ids"]
                related_text_ids.extend(expression_ids)
            else:
                commentary_ids = text_related_by_work_response[key]["expression_ids"]
                commentary_text_ids.extend(commentary_ids)
        if text["type"] not in ['commentary', 'sibling_commentary']:
            related_text_ids.append(text_id)
        else:
            commentary_text_ids.append(text_id)
        print("related_text_ids:>>>>>>>>>>>" , related_text_ids)
        print("commentary_text_ids:>>>>>>>>>>>" , commentary_text_ids)
        await self.get_text_meta_data_service(text_ids=related_text_ids, type="translation", token=token)
        # await self.get_text_meta_data_service(text_ids=commentary_text_ids, type="commentary", token=token, category_group_id=version_group_id)


    async def get_text_meta_data_service(self, text_ids: List[str], type: str, category_group_id: str = None):
        
        for text_id in text_ids:
            text_metadata = await get_text_metadata(text_id)

            is_text_uploaded = await self.is_text_uploaded(text_id)
            if is_text_uploaded:
                print(f"Skipping already uploaded text: {text_id}")
                continue



    async def get_text_critical_instance(text_id: str) -> CriticalInstanceResponse:
        critical_instances_response = await get_critical_instances(text_id)
        critical_instances_list = critical_instances_response.critical_instances
        return CriticalInstanceResponse(critical_instances=critical_instances_list)

    async def is_text_uploaded(self, text_id: str) -> bool:
        text_critical_instance = await self.get_text_critical_instance(text_id)
        instance_id = text_critical_instance.critical_instances[0].id
        

