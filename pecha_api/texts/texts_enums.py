from enum import Enum

class TextType(Enum):
    RECITATION = "recitation"
    COMMENTARY = "commentary"
    VERSION = "version"
    SHEET = "sheet"

class PaginationDirection(Enum):
    NEXT = "next"
    PREVIOUS = "previous"