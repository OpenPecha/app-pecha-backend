from .texts_repository import get_texts_by_id, get_texts_by_category
from .texts_response_models import TextResponse, TextModel, Category, TextsCategoryResponse, Text


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

async def get_text_by_category(category: str, language: str, skip: int, limit: int):
    category = Category(
        id= "d19338e",
        title= "Bodhicaryavatara",
        description= "Bodhicaryavatara title",
        slug= "bodhicaryavatara",
        has_child= False
    )
    texts = await get_texts_by_category(category=category, language=language, skip=skip, limit=limit)
    text_list = [
        Text(
            id= texts.id,
            title = texts.title,
            language= texts.language,
            type= texts.type,
            is_published= texts.is_published,
            created_date= texts.created_date,
            updated_date= texts.updated_date,
            published_date= texts.published_date,
            published_by= texts.published_by
        )
        for text in texts
    ]
    return TextsCategoryResponse(category=category, texts=text_list, total=len(text_list), skip=skip, limit=limit)