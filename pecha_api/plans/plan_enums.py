import enum
from sqlalchemy import Enum

class DifficultyLevel(enum.Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

class ContentType(enum.Enum):
    TEXT = "TEXT"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    IMAGE = "IMAGE"
    SOURCE_REFERENCE = "SOURCE_REFERENCE"

class UserPlanStatus(enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"

class PlanStatus(enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"
    UNDER_REVIEW = "UNDER_REVIEW"

class LanguageCode(enum.Enum):
    EN = "en"
    BO = "bo"
    ZH = "zh"

# SQLAlchemy enum types
DifficultyLevelEnum = Enum(DifficultyLevel)
ContentTypeEnum = Enum(ContentType)
UserPlanStatusEnum = Enum(UserPlanStatus)
PlanStatusEnum = Enum(PlanStatus)
LanguageCodeEnum = Enum(LanguageCode)


class DifficultyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class UnlockCondition(str, Enum):
    sequential = "sequential"
    date_based = "date_based"


class ContentType(str, Enum):
    text = "text"
    audio = "audio"
    video = "video"
    image = "image"
    source_reference = "source_reference"


class UserPlanStatus(str, Enum):
    not_started = "not_started"
    active = "active"
    paused = "paused"
    completed = "completed"
    abandoned = "abandoned"

   
