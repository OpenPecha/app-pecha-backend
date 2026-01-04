import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from pecha_api.text_uploader.segments.segment_service import SegmentService


def test_get_annotation_ids_filters_segmentation_only():
    service = SegmentService()
    instance = {
        "annotations": [
            {"type": "note", "annotation_id": "a0"},
            {"type": "segmentation", "annotation_id": "a1"},
            {"type": "segmentation", "annotation_id": "a2"},
        ]
    }

    assert service.get_annotation_ids(instance) == ["a1", "a2"]


def test_get_annotation_ids_handles_none_annotations():
    service = SegmentService()
    assert service.get_annotation_ids({"annotations": None}) == []


def test_parse_segments_content_slices_base_text():
    service = SegmentService()
    base_text = "abcdef"
    segments_annotation = [
        {"id": "s1", "span": {"start": 0, "end": 2}},
        {"id": "s2", "span": {"start": 2, "end": 6}},
    ]

    assert service.parse_segments_content(segments_annotation, base_text) == [
        {"segment_id": "s1", "content": "ab"},
        {"segment_id": "s2", "content": "cdef"},
    ]


@pytest.mark.asyncio
async def test_is_text_segments_uploaded_true_when_any_segments_exist():
    service = SegmentService()
    with patch(
        "pecha_api.text_uploader.segments.segment_service.get_segments_by_text_id",
        new_callable=AsyncMock,
        return_value=[{"id": "seg_1"}],
    ):
        assert await service.is_text_segments_uploaded("text_1") is True


@pytest.mark.asyncio
async def test_upload_bulk_segments_batches_and_posts_payload():
    service = SegmentService()
    text_upload_request = SimpleNamespace(destination_url="https://dest.example")
    token = "t0k3n"

    # 401 segments -> two batches (400 + 1)
    segments_content = [
        {"segment_id": f"s{i}", "content": f"c{i}"} for i in range(401)
    ]

    with patch(
        "pecha_api.text_uploader.segments.segment_service.post_segments",
        new_callable=AsyncMock,
        return_value={"ok": True},
    ) as mock_post_segments:
        await service.upload_bulk_segments(
            text_id="text_1",
            segments_content=segments_content,
            text_upload_request=text_upload_request,
            token=token,
        )

        assert mock_post_segments.await_count == 2

        first_payload = mock_post_segments.await_args_list[0].args[0]
        second_payload = mock_post_segments.await_args_list[1].args[0]

        assert first_payload["text_id"] == "text_1"
        assert len(first_payload["segments"]) == 400
        assert first_payload["segments"][0] == {
            "pecha_segment_id": "s0",
            "content": "c0",
            "type": "source",
        }

        assert second_payload["text_id"] == "text_1"
        assert len(second_payload["segments"]) == 1
        assert second_payload["segments"][0] == {
            "pecha_segment_id": "s400",
            "content": "c400",
            "type": "source",
        }

        # Verify destination/token plumbing (payload, destination_url, token)
        assert mock_post_segments.await_args_list[0].args[1:] == (
            "https://dest.example",
            token,
        )


