from enum import Enum



APPLICATION = "webuddhist"

ACCESS_TOKEN = "1234567890"

COLLECTION_LANGUAGES = ["bo", "en", "zh"]

class TextType(Enum):
    COMMENTARY = "commentary"
    ROOT = "root"
    TRANSLATION = "translation"
    TRANSLATION_SOURCE = "translation_source"
    NONE = None

VERSION_TEXT_TYPE = [TextType.TRANSLATION.value, TextType.ROOT.value, TextType.TRANSLATION_SOURCE.value, TextType.NONE.value, TextType.ROOT.value]


class OpenPechaAPIURL(Enum):
    DEVELOPMENT = "https://api-aq25662yyq-uc.a.run.app"

class SQSURL(Enum):
    DEVELOPMENT = "https://sqs-uploader-service.onrender.com"


class DestinationURL(Enum):
    STAGING = "https://webuddhist-tst-backend.onrender.com/api/v1"
    LOCAL = "http://localhost:8000/api/v1"

