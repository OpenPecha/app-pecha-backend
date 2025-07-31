from enum import Enum

class CacheType(Enum):
    TEXT_DETAIL = "text_detail"
    TEXT_VERSIONS = "text_versions"
    TEXTS_BY_COLLECTION = "texts_by_collection"
    TEXT_TABLE_OF_CONTENTS = "text_table_of_contents"
    DETAIL_TEXT_TABLE_OF_CONTENT = "detail_text_table_of_content"

    SEGMENT_DETAIL = "segment_detail"
    SEGMENT_INFO = "segment_info"
    SEGMENT_ROOT_TEXT = "segment_root_text"
    SEGMENT_TRANSLATIONS = "segment_translations"
    SEGMENT_COMMENTARIES = "segment_commentaries"

    GROUP_DETAIL = "group_detail"

    SHEETS = "sheets"
    SHEET_DETAIL = "sheet_detail"