from typing import List, Tuple, Optional
from pecha_api.recitations.recitations_response_models import RecitationDTO

def apply_search_recitation_title_filter(texts: List[RecitationDTO], search: Optional[str]) -> List[RecitationDTO]:
    filtered_texts = []
    for text in texts:
        if search:
            if search.lower() in text.title.lower():
                filtered_texts.append(text)
        else:
            filtered_texts.append(text)
    return filtered_texts