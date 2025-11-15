import enum

class RecitationTextType(enum.Enum):
    VERSION = "version"
    ADAPTATION = "adaptation"

class RecitationListTextType(enum.Enum):
    RECITATIONS = "recitations"
    TRANSLATIONS = "translations"
    TRANSLITERATIONS = "transliterations"
    ADAPTATIONS = "adaptations"