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
DifficultyLevelEnum = Enum(DifficultyLevel, name="difficulty_level")
ContentTypeEnum = Enum(ContentType, name="content_type")
UserPlanStatusEnum = Enum(UserPlanStatus, name="user_plan_status")
PlanStatusEnum = Enum(PlanStatus, name="plan_status")
LanguageCodeEnum = Enum(LanguageCode, name="language_code")



