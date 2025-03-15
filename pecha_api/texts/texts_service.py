
from .texts_repository import get_texts_by_id, get_contents_by_id, get_text_by_id, get_versions_by_id, get_texts_by_category, get_versions_by_id, create_text, create_segment
from .texts_response_models import TableOfContentResponse, TextResponse, TextModel, TextVersionResponse, TextVersion, Category, TextsCategoryResponse, Text, CreateTextRequest, CreateSegmentRequest


from pecha_api.config import get

async def get_texts_by_category_id(category: str, language: str, skip: int, limit: int):
    texts = await get_texts_by_category(category=category, language=language, skip=skip, limit=limit)
    text_list = [
        Text(
            id=text["id"],
            title=text["title"],
            language=text["language"],
            type=text["type"],
            is_published=text["is_published"],
            created_date=text["created_date"],
            updated_date=text["updated_date"],
            published_date=text["published_date"],
            published_by=text["published_by"]
        )
        for text in texts
    ]
    return text_list

async def get_texts_without_category():
    root_text, text_versions = get_texts_by_id()
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
  

async def get_text_by_term_or_category(
        category: str,
        language: str,
        skip: int,
        limit: int
    ):
    if language is None:
        language = get("DEFAULT_LANGUAGE")

    if category is not None:
        term = Category(
            id= "d19338e",
            title= "Bodhicaryavatara",
            description= "Bodhicaryavatara title",
            slug= "bodhicaryavatara",
            has_child= False
        )
        texts = await get_texts_by_category_id(category=category, language=language, skip=skip, limit=limit)
        return TextsCategoryResponse(
            category=term,
            texts=texts,
            total=len(texts),
            skip=skip,
            limit=limit
        )
    else:
        return await get_texts_without_category()

async def get_contents_by_text_id(text_id: str, skip:int, limit: int) -> TableOfContentResponse:
    list_of_sections = await get_contents_by_id(text_id=text_id, skip=skip, limit=limit)
    return TableOfContentResponse(
        id="5894c3b8-4c52-4964-b0d1-9498a71fd1e1",
        text_id=text_id,
        segments=list_of_sections
    )

async def get_versions_by_text_id(text_id: str, skip: int, limit: int) -> TextVersionResponse:
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

async def create_new_text(create_text_request: CreateTextRequest):
    new_text = await create_text(create_text_request=create_text_request)
    return new_text

async def create_new_segment(create_segment_request: CreateSegmentRequest):
    new_segment = await create_segment(create_segment_request=create_segment_request)
    return new_segment
