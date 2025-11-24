from enum import Enum

class TextType(Enum):
    ROOT_TEXT = "root_text"
    COMMENTARY = "commentary"
    VERSION = "version"
    SHEET = "sheet"
    TRANSLATION = "translation"
    TRANSLITERATION = "transliteration"
    ADAPTATION = "adaptation"

class TextTypes(Enum):
    VERSIONS = "versions"

class PaginationDirection(Enum):
    NEXT = "next"
    PREVIOUS = "previous"

class FallbackTextLanguage(Enum):
    EN = "en"
    BO = "bo"
    ZH = "zh"