from .texts_repository import get_texts_by_id
from .texts_response_models import TextResponse, TextModel, CreateTextRequest, CreateSegmentRequest
from .texts_repository import create_text, create_segment

from pecha_api.config import get
def get_text_by_term(language: str):
    root_text, text_versions = get_texts_by_id()
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    return TextResponse(
        source=TextModel(
            id=str(root_text.id),
            title=root_text.titles[language],
            summary=root_text.summaries[language],
            language=root_text.default_language,
            source='',
            parent_id=''
        ),
        versions=[
            TextModel(
                id=str(text.id),
                title=text.titles[text.default_language],
                summary=text.summaries[text.default_language],
                language=text.default_language,
                source='',
                parent_id=str(root_text.id)
            )
            for text in text_versions
        ]
    )

async def create_new_text(create_text_request: CreateTextRequest):
    new_text = await create_text(create_text_request=create_text_request)
    return new_text

async def create_new_segment(text_id: str, create_segment_request: CreateSegmentRequest):
    new_segment = await create_segment(text_id=text_id, create_segment_request=create_segment_request)
    return new_segment