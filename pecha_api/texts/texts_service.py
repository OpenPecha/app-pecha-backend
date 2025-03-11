from .texts_repository import get_texts_by_id, get_contents_by_id, get_text_by_id, get_versions_by_id
from .texts_response_models import TableOfContentResponse, TextResponse, TextModel, TextVersionResponse, TextVersion

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

async def get_contents_by_text_id(text_id: str, skip:int, limit: int) -> TableOfContentResponse:
    list_of_sections = await get_contents_by_id(text_id=text_id, skip=skip, limit=limit)
    return TableOfContentResponse(
        id="5894c3b8-4c52-4964-b0d1-9498a71fd1e1",
        text_id=text_id,
        segments=list_of_sections
    )

async def get_version_by_text_id(text_id: str, skip: int, limit: int) -> TextVersionResponse:
    root_text = await get_text_by_id(text_id=text_id)
    versions = await get_versions_by_id(text_id=text_id, skip=skip, limit=limit)
    list_of_version = [
        TextVersion(
            id=version["id"],
            title=version["title"],
            parent_id=version["parent_id"],
            priority=version["priority"],
            language=version["language"],
            type=version["type"],
            is_published=version["is_published"],
            created_date=version["created_date"],
            updated_date=version["updated_date"],
            published_date=version["published_date"],
            published_by=version["published_by"]
        )
        for version in versions
    ]
    return TextVersionResponse(
        text=root_text,
        versions=list_of_version
    )