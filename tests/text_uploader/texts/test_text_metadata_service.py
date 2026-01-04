import pytest
from unittest.mock import AsyncMock, patch

from pecha_api.text_uploader.text_metadata.text_metadata_service import TextMetadataService
from pecha_api.text_uploader.text_metadata.text_metadata_model import (
    CriticalInstance,
    CriticalInstanceResponse,
)


@pytest.mark.asyncio
async def test_create_textmetada_payload_version_sets_group_and_category_from_collection():
    service = TextMetadataService()
    service.version_group_id = "group_v1"

    text_metadata = {
        "language": "en",
        "title": {"en": "A Title"},
        "category_id": "pecha_cat_1",
        "isPublished": True,
        "views": 12,
        "ranking": 3,
        "license": "CC0",
    }

    with patch.object(
        service,
        "get_text_critical_instance",
        new_callable=AsyncMock,
        return_value=CriticalInstanceResponse(
            critical_instances=[
                CriticalInstance(
                    id="inst_1",
                    type="critical",
                    source="https://source.example",
                )
            ]
        ),
    ), patch(
        "pecha_api.text_uploader.text_metadata.text_metadata_service.get_collection_id_by_pecha_collection_id",
        new_callable=AsyncMock,
        return_value="wb_cat_1",
    ):
        payload = await service.create_textmetada_payload(
            text_id="t1",
            text_metadata=text_metadata,
            type="version",
        )

    assert payload.pecha_text_id == "inst_1"
    assert payload.title == "A Title"
    assert payload.language == "en"
    assert payload.group_id == "group_v1"
    assert payload.categories == ["wb_cat_1"]
    assert payload.type == "version"
    assert payload.source_link == "https://source.example"


@pytest.mark.asyncio
async def test_create_textmetada_payload_commentary_sets_group_and_category_from_version_group():
    service = TextMetadataService()
    service.version_group_id = "group_v1"
    service.commentary_group_id = "group_c1"

    text_metadata = {
        "language": "bo",
        "title": {"bo": "མཚན་བྱང་"},
    }

    with patch.object(
        service,
        "get_text_critical_instance",
        new_callable=AsyncMock,
        return_value=CriticalInstanceResponse(
            critical_instances=[
                CriticalInstance(
                    id="inst_c1",
                    type="critical",
                    source="s",
                )
            ]
        ),
    ):
        payload = await service.create_textmetada_payload(
            text_id="t_commentary",
            text_metadata=text_metadata,
            type="commentary",
        )

    assert payload.group_id == "group_c1"
    assert payload.categories == ["group_v1"]
    assert payload.type == "commentary"


@pytest.mark.asyncio
async def test_get_uploaded_texts_returns_uploaded_text_ids_and_instances_mapping():
    service = TextMetadataService()

    async def _get_critical_instance_side_effect(text_id: str):
        instance_id = {"t1": "inst_1", "t2": "inst_2"}[text_id]
        return CriticalInstanceResponse(
            critical_instances=[
                CriticalInstance(
                    id=instance_id,
                    type="critical",
                    source="src",
                )
            ]
        )

    # Only inst_2 is already uploaded in the destination DB
    uploaded_text_row = type("Row", (), {"pecha_text_id": "inst_2", "group_id": "g"})()

    with patch.object(
        service,
        "get_text_critical_instance",
        new_callable=AsyncMock,
        side_effect=_get_critical_instance_side_effect,
    ), patch(
        "pecha_api.text_uploader.text_metadata.text_metadata_service.get_texts_by_pecha_text_ids",
        new_callable=AsyncMock,
        return_value=[uploaded_text_row],
    ):
        texts, uploaded_text_ids, instances = await service.get_uploaded_texts(
            ["t1", "t2"]
        )

    assert texts == [uploaded_text_row]
    assert uploaded_text_ids == ["t2"]
    assert instances == {"t1": "inst_1", "t2": "inst_2"}


@pytest.mark.asyncio
async def test_get_wb_collection_id_raises_when_collection_missing():
    service = TextMetadataService()
    with patch(
        "pecha_api.text_uploader.text_metadata.text_metadata_service.get_collection_id_by_pecha_collection_id",
        new_callable=AsyncMock,
        return_value=None,
    ):
        with pytest.raises(
            ValueError, match="Collection with pecha_collection_id pecha_missing not found"
        ):
            await service.get_wb_collection_id("pecha_missing")


