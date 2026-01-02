from typing import Any, List
from uuid import uuid4 as uuid
import json
import logging

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
from pecha_api.texts.texts_repository import get_texts_by_pecha_text_ids


logging.basicConfig(level=logging.INFO)

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
        await self.get_text_meta_data_service(text_ids=related_text_ids, type="translation", token=token)
        # await self.get_text_meta_data_service(text_ids=commentary_text_ids, type="commentary", token=token, category_group_id=version_group_id)


    async def get_text_meta_data_service(self, text_ids: List[str], type: str, token: str):

        

        uploaded_texts, uploaded_text_ids = await self.get_uploaded_texts(text_ids)

        if len(uploaded_texts) > 0 and type == "translation":
            group_id = uploaded_texts[0].group_id
            self.version_group_id = group_id

        for text_id in text_ids:
            text_metadata = await get_text_metadata(text_id)
            language = text_metadata['language']
            title = text_metadata['title'][language]
            category = text_metadata['category_id']

            if text_id in uploaded_text_ids:
                logging.info(f"Skipping already uploaded text: {title}")
                continue

            if type == "translation":
                if not self.version_group_id:
                    group_response = await post_group('text')
                    self.version_group_id = group_response["id"]
                    logging.info(f"Created new group {group_response['id']} for translation")

                payload = await self.create_textmetada_payload(text_id, text_metadata, category, type="version")
                print("payload:>>>>>>>>>>>" , payload)

            elif type == "commentary":
                group_response = await post_group('commentary')
                self.commentary_group_id = group_response["id"]
                logging.info(f"Created new group {group_response['id']} for commentary")

            
           


    async def create_textmetada_payload(self, text_id: str, text_metadata: dict[str, Any], category: str, type: str):
        language = text_metadata['language']
        title = text_metadata['title'][language]
        instance = await self.get_text_critical_instance(text_id)

        if type == "version":
            category_id = text_metadata.get("category_id", "")
            category_ids = [category_id]
            group_id = self.version_group_id
        elif type == "commentary":
            category_ids = [self.version_group_id]
            group_id = self.commentary_group_id

        return TextGroupPayload(
            pecha_text_id=instance.critical_instances[0].id,
            title=title,
            language=language,
            isPublished=text_metadata.get("isPublished", True),
            group_id=group_id,
            published_by="",
            type=type,
            categories=category_ids,  
            views=text_metadata.get("views", 0),
            source_link=instance.critical_instances[0].source,
            ranking=text_metadata.get("ranking"),
            license=text_metadata.get("license"),
        )



    async def get_text_critical_instance(self, text_id: str) -> CriticalInstanceResponse:
        critical_instances_response = await get_critical_instances(text_id)
        critical_instances_list = critical_instances_response.critical_instances
        return CriticalInstanceResponse(critical_instances=critical_instances_list)

    async def get_uploaded_texts(self, text_ids: List[str]):
        instances = {}
        for text_id in text_ids:
            text_critical_instance = await self.get_text_critical_instance(text_id)
            instance_id = text_critical_instance.critical_instances[0].id
            instances[instance_id] = text_id
        
        instance_ids = instances.keys()
        texts = await get_texts_by_pecha_text_ids(instance_ids)
        pecha_text_ids = [text.pecha_text_id for text in texts]
        uploaded_pecha_text_ids = [instances[id] for id in instance_ids if id in pecha_text_ids]

        return texts, uploaded_pecha_text_ids


