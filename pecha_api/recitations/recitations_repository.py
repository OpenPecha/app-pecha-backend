from typing import List, Tuple, Optional

def apply_search_recitation_title_filter(text: List[Tuple[str, str]], search: Optional[str]):
    text = [text for text in text if search.lower() in text[1].lower()]
    return text