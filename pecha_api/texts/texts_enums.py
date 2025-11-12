from enum import Enum

class TextType(Enum):
    COMMENTARY = "commentary"
    VERSION = "version"
    SHEET = "sheet"

class PaginationDirection(Enum):
    NEXT = "next"
    PREVIOUS = "previous"