from enum import Enum

class TextType(Enum):
    RECITATION = "recitation"
    COMMENTARY = "commentary"
    VERSION = "version"
    SHEET = "sheet"
    TRANSLATION = "translation"
    TRANSLITERATION = "transliteration"
    ADAPTATION = "adaptation"

class PaginationDirection(Enum):
    NEXT = "next"
    PREVIOUS = "previous"