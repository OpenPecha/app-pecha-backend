from .texts_repository import get_texts_by_id
from .texts_response_models import TextResponse, TextModel

from pecha_api.config import get
def get_text_by_term(term_id: str, language: str):
    root_text, text_versions = get_texts_by_id()
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    TextResponse(
        source=TextModel(
            id=root_text.id,
            title=root_text.titles[language],
            summary=root_text.summaries[language],
            language=root_text.default_language,
            source='',
            parent_id=''
        ),
        versions=[
            TextModel(
                id=text.id,
                title=text.titles[text.default_language],
                summary=text.summaries[text.default_language],
                language=text.default_language,
                source='',
                parent_id=root_text.id
            )
            for text in text_versions
        ]
    )
