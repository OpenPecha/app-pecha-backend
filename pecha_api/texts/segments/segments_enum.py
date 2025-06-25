from enum import Enum

class SegmentType(Enum):
    SOURCE = "text"
    CONTENT = "content"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"