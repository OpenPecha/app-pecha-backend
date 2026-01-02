from typing import Any, List
from uuid import uuid4 as uuid
import json

from pecha_api.text_uploader.text_uploader_response_model import TextUploadRequest

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
        # version_group_id = await self.get_text_meta_data_service(text_ids=related_text_ids, type="translation", token=token)
        # await self.get_text_meta_data_service(text_ids=commentary_text_ids, type="commentary", token=token, category_group_id=version_group_id)


    async def get_text_meta_data_service(self, text_ids: List[str], type: str, category_group_id: str = None):
        
        # Initialize version_group_id
        version_group_id = None
        
        if type == "translation":
            # Check if any text_id already has a version_group_id in the CSV
            for text_id in text_ids:
                # version_group_id = get_log_group_id_by_pecha_text_id(text_id)
                if version_group_id:
                    print(f"Reusing existing version_group_id: {version_group_id} for text_id: {text_id}")
                    break
            
        
        for text_id in text_ids:
            text_metadata = await get_text_metadata(text_id)
            
            # Extract category from text_metadata
            category = text_metadata.get("category_id", "")
            
            if type == "translation":
                if not version_group_id:
                    group_response = await post_group('text')
                    version_group_id = group_response["id"]
                    print(f"Created new group {group_response['id']}, category_id={category}")
                
                await self.create_text_db(pecha_text_id=text_id, text_metadata=text_metadata, type='text', group_id=version_group_id, category_id=category, log_group_id=version_group_id)
                
            elif type == "commentary":
                commentary_group = await post_group('commentary')
                commentary_group_id = commentary_group["id"]
                await self.create_text_db(pecha_text_id=text_id, text_metadata=text_metadata, type='commentary', group_id=commentary_group_id, category_id=category, log_group_id=None, commentary_group_id=category_group_id)
        
        return version_group_id

    async def create_text_db(self, pecha_text_id: str, text_metadata: dict[str, Any], type: str, group_id: str, category_id: str = "", log_group_id: str = None, commentary_group_id: str = None):
        if type == "text":
            text_payload = await self._filter_text_groups(text_metadata, group_id, type="version")
            if text_payload is None:
                return
            instance_id = text_payload.pecha_text_id

            # Skip upload if this text was already uploaded (checked via CSV log).
            if instance_id and has_been_uploaded_by_instance_id(instance_id, text_payload.type):
                print(f"Skipping already uploaded version text: {instance_id} >>> ({text_payload.title})"
                )
                return
            text_response = await post_text(text_payload)
            if instance_id:
                log_uploaded_text(
                    instance_id=instance_id,
                    pecha_text_id=pecha_text_id,
                    text_id=text_response["id"],
                    text_type=text_payload.type,
                    title=text_payload.title,
                    language=text_payload.language,
                    source_link=text_payload.source_link,
                    category_id=category_id,
                    version_group_id=group_id,
                    log_group_id=log_group_id,
                )
        else:
            text_payload = await self._filter_text_groups(text_metadata, group_id, type="commentary", commentary_group_id=commentary_group_id)

            if text_payload is None:
                return
            instance_id = text_payload.pecha_text_id
            if instance_id and has_been_uploaded_by_instance_id(instance_id, text_payload.type):
                print(f"Skipping already uploaded commentary text: {instance_id} >>> ({text_payload.title})")
                return
            text_response = await post_text(text_payload)
            if instance_id:
                log_uploaded_text(
                    instance_id=instance_id,
                    pecha_text_id=pecha_text_id,
                    text_id=text_response["id"],
                    text_type=text_payload.type,
                    title=text_payload.title,
                    language=text_payload.language,
                    source_link=text_payload.source_link,
                    category_id=category_id,
                    version_group_id=group_id,
                    log_group_id=log_group_id,
                )

    def group_instances_by_type(self, instances: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        versions: list[dict[str, Any]] = []
        commentaries: list[dict[str, Any]] = []
        for instance in instances:
            if instance["relationship"] == "translation" or instance["relationship"] == "translation_source":
                versions.append(instance)
            elif instance["relationship"] == "commentary":
                commentaries.append(instance)
        return {"text": versions, "commentary": commentaries}

    async def upload_text_groups(self) -> dict[str, list[dict[str, Any]]]:
        texts = await self.get_text_groups_service()
        for text in texts:
            data = await get_text_instances(text["id"], type="critical")
            instance_id = data[0]["id"]
            get_related_texts_response = await get_related_texts(instance_id)

            grouped_text_by_type = self.group_instances_by_type(get_related_texts_response)
            
            # Upload groups to webuddhist backend
            for key in grouped_text_by_type.keys():
                group_response = await post_group(key)
                if key == "text":
                    self.version_group_id = group_response["id"]
                elif key == "commentary":
                    self.commentary_group_id = group_response["id"]

            # Upload texts to webuddhist backend
            for text in grouped_text_by_type["text"]:
                text_payload = await self._filter_text_groups(
                    text, self.version_group_id, type="version"
                )
                

            for text in grouped_text_by_type["commentary"]:
                text_payload = await self._filter_text_groups(
                    text,
                    self.commentary_group_id,
                    type="commentary"
                )
                pecha_id = text_payload.pecha_text_id

                if pecha_id and has_been_uploaded_by_instance_id(pecha_id, text_payload.type):
                    print(f"Skipping already uploaded commentary text: {pecha_id} ({text_payload.title})")
                    continue

                text_response = await post_text(text_payload)
        
                if pecha_id:
                    log_uploaded_text(
                        pecha_text_id=pecha_id,
                        text_id=text_response["id"],
                        text_type=text_payload.type,
                        title=text_payload.title,
                        language=text_payload.language,
                        source_link=text_payload.source_link,
                        category_id="",
                        version_group_id=self.commentary_group_id,
                        log_group_id=None,
                    )

        return grouped_text_by_type

    async def get_texts_service(self, type: str | None = None):
        return await get_texts(type)

    async def _filter_text_groups(
        self, text: dict[str, Any], group_id: str | None, type: str, commentary_group_id: str = None
    ) -> TextGroupPayload:
        # Fetch critical instances for this text so we can map ID and source.
        critical_instances_list = await get_critical_instances(text["id"])

        if len(critical_instances_list) > 0:
            critical_instance = critical_instances_list[0]
        else:
            return None

        raw_title = ''

        for title in text["title"].values():
            raw_title = title
            break

    

        # Look up the collection ID from collection_upload_log by category_id (pecha_collection_id)
        category_ids = []
        if text["category_id"] and type == "version":
            id = get_parent_id_by_pecha_collection_id(text["category_id"])
            category_ids.append(id)
        elif text["category_id"] and type == "commentary":
            # Get version_group_id from CSV by matching category_id
            version_group_id = commentary_group_id
            if version_group_id:
                category_ids.append(version_group_id)

        if 'Translation' in raw_title:
            raw_title = raw_title.replace("Translation", "༼ཁ་སྐད།༽")
        
        return TextGroupPayload(
            pecha_text_id=critical_instance["id"],
            title=raw_title,
            language=text.get("language"),
            isPublished=text.get("isPublished", False),
            group_id=group_id,
            published_by="",
            type=type,
            categories=category_ids,  
            views=text.get("views", 0),
            source_link=critical_instance["source"],
            ranking=text.get("ranking"),
            license=text.get("license"),
        )

    def _extract_collection_id(self, data: Any) -> str | None:
        """
        Normalise a collection API response into a single string ID.

        The `/collections` endpoint may return:
          - a single object with `id`, `_id`, or `collection_id`
          - a list of such objects
          - a wrapper object like `{"collections": [ ... ]}`
        This helper tries to handle all of those cases and returns the first
        usable ID as a string, or `None` if none can be found.
        """
        # If we were given a list, look at the first element.
        if isinstance(data, list):
            if not data:
                return None
            data = data[0]

        # If the response is wrapped, unwrap the first collection item.
        if isinstance(data, dict) and "collections" in data:
            collections = data.get("collections") or []
            if isinstance(collections, list) and collections:
                return self._extract_collection_id(collections[0])

        if not isinstance(data, dict):
            return None

        raw_id = data.get("id") or data.get("_id") or data.get("collection_id")

        if isinstance(raw_id, dict) and "$oid" in raw_id:
            return str(raw_id["$oid"])
        if raw_id is not None:
            return str(raw_id)

        return None

    def group_texts_by_type(
        self, groups_payload: dict[str, Any]
    ) -> dict[str, list[dict[str, Any]]]:
        texts = groups_payload.get("texts", [])

        versions: list[dict[str, Any]] = []
        commentaries: list[dict[str, Any]] = []

        for item in texts:
            item_type = item["type"]

            # Only keep root and translation in versions.
            if item_type in {TextType.TRANSLATION.value, TextType.ROOT.value, TextType.TRANSLATION_SOURCE.value}:
                versions.append(item)
            elif item_type == TextType.COMMENTARY.value:
                commentaries.append(item)

        return {
            "text": versions,
            "commentary": commentaries,
        }


    async def get_text_related_by_work_service(text_id: str):
        pass