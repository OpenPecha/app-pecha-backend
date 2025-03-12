from .texts_repository import get_texts_by_id, get_texts_by_category
from .texts_response_models import TextResponse, TextModel, Category, TextsCategoryResponse, Text


from pecha_api.config import get
async def get_text_by_term_or_category(
        category: str,
        language: str,
        skip: int,
        limit: int
    ):
    if language is None:
        language = get("DEFAULT_LANGUAGE")

    if category is not None:
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
                id= text["id"],
                title = text["title"],
                language= text["language"],
                type= text["type"],
                is_published= text["is_published"],
                created_date= text["created_date"],
                updated_date= text["updated_date"],
                published_date= text["published_date"],
                published_by= text["published_by"]
            )
            for text in texts
        ]
        return TextsCategoryResponse(category=category, texts=text_list, total=len(text_list), skip=skip, limit=limit)
        
    
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

# async def get_text_by_category(category: str, language: str, skip: int, limit: int):
#     category = Category(
#         id= "d19338e",
#         title= "Bodhicaryavatara",
#         description= "Bodhicaryavatara title",
#         slug= "bodhicaryavatara",
#         has_child= False
#     )
#     texts = await get_texts_by_category(category=category, language=language, skip=skip, limit=limit)
#     text_list = [
#         Text(
#             id= text["id"],
#             title = text["title"],
#             language= text["language"],
#             type= text["type"],
#             is_published= text["is_published"],
#             created_date= text["created_date"],
#             updated_date= text["updated_date"],
#             published_date= text["published_date"],
#             published_by= text["published_by"]
#         )
#         for text in texts
#     ]
#     return TextsCategoryResponse(category=category, texts=text_list, total=len(text_list), skip=skip, limit=limit)