from uuid import uuid4
from typing import Iterable

from pecha_api.plans.plan_response_model import (
    PlanAuthorDetails,
    PlanListDetails,
    PlanRequest,
    PlanResponse,
)
from typing import Optional


def _generate_mock_plans(total: int = 100) -> list[dict[str, object]]:
    difficulty_levels = ["beginner", "intermediate", "advanced"]
    sample_tags = [
        "mindfulness",
        "buddhism",
        "meditation",
        "philosophy",
        "ethics",
        "compassion",
    ]

    plans: list[dict[str, object]] = []
    for i in range(total):
        author: dict[str, object] = {
            "id": uuid4(),
            "email": f"author{i}@example.com",
            "image_url": f"https://example.com/image{i}.jpg",
        }

        plan: dict[str, object] = {
            "id": uuid4(),
            "title": f"Plan {i}",
            "description": f"Description for plan {i}",
            "author_id": author,
            "language": "en",
            "difficulty_level": difficulty_levels[i % len(difficulty_levels)],
            "tags": [sample_tags[i % len(sample_tags)], sample_tags[(i + 2) % len(sample_tags)]],
            "featured": i % 5 == 0,
            "is_active": True,
            "image_url": f"https://example.com/image{i}.jpg",
            "plan_days": (i % 7) + 1,
            "plan_used_count": (i * 3) % 100,
        }
        plans.append(plan)
    return plans


def _matches_difficulty(item: dict[str, object], difficulty_level: str | None) -> bool:
    if not difficulty_level:
        return True
    return str(item.get("difficulty_level")) == difficulty_level


def _matches_featured(item: dict[str, object], featured: bool | None) -> bool:
    if featured is None:
        return True
    return bool(item.get("featured")) is featured


def _matches_tags(item: dict[str, object], tags: list[str] | None) -> bool:
    if not tags:
        return True
    item_tags = {str(t) for t in item.get("tags", [])}
    query_tags = {str(t) for t in tags}
    return len(item_tags.intersection(query_tags)) > 0


def get_plan_list(difficulty_level: Optional[str] = None, tags: Optional[list[str]] = None, featured: Optional[bool] = None, skip: int = 0, limit: int = 10) -> PlanResponse:
    all_plans = _generate_mock_plans(total=200)

    filtered = [
        p
        for p in all_plans
        if _matches_difficulty(p, difficulty_level)
        and _matches_featured(p, featured)
        and _matches_tags(p, tags)
    ]

    total = len(filtered)
    start = skip if skip >= 0 else 0
    end = start + limit if limit > 0 else start
    paginated = filtered[start:end]

    response = PlanResponse(
        plan=[PlanListDetails(**p) for p in paginated],
        total=total,
        skip=skip,
        limit=limit,
    )
    return response
