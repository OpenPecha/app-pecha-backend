from enum import Enum


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


