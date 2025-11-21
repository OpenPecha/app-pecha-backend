from typing import List, Tuple, Optional

def apply_search_recitation_title_filter(text_title: str, search: Optional[str]):
    if search:
        if search.lower() in text_title.lower():
            return text_title
        else:
            return None
    return text_title