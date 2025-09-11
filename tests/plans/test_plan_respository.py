import os
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pecha_api.db.database import Base
from pecha_api.plans.plans_models import Plan
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.plans.users.user_plan_progress_models import UserPlanProgress
from pecha_api.plans.authors.plan_author_model import Author
from pecha_api.plans.plans_repository import save_plan, get_plans


DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not DATABASE_URL:
    pytest.skip(
        "Set TEST_DATABASE_URL to a PostgreSQL database URL to run these tests.",
        allow_module_level=True,
    )

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db():
    # Create only the plans-related tables needed for these tests
    Base.metadata.create_all(
        bind=engine,
        tables=[Author.__table__, Plan.__table__, PlanItem.__table__, UserPlanProgress.__table__],
    )
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(
        bind=engine,
        tables=[Author.__table__, Plan.__table__, PlanItem.__table__, UserPlanProgress.__table__],
    )


def _create_author(db) -> Author:
    author = Author(
        first_name="First",
        last_name="Last",
        email=f"{uuid.uuid4()}@example.com",
        password="secret",
        created_by="tester",
    )
    db.add(author)
    db.commit()
    db.refresh(author)
    return author


def test_save_plan_success(db):
    author = _create_author(db)

    plan = Plan(
        title="Mindfulness Basics",
        description="A simple plan.",
        author_id=author.id,
        created_by="tester",
    )

    saved = save_plan(db, plan)

    assert saved.id is not None
    assert saved.title == "Mindfulness Basics"
    assert saved.author_id == author.id


def test_get_plans_filter_sort_and_pagination(db):
    author = _create_author(db)

    # Seed multiple plans
    titles = ["B Plan", "A Plan", "C Plan"]
    for t in titles:
        p = Plan(
            title=t,
            description=f"{t} description",
            author_id=author.id,
            created_by="tester",
        )
        save_plan(db, p)

    # Sort by status ascending (all defaults are DRAFT)
    rows, total = get_plans(
        db=db,
        search=None,
        sort_by="status",
        sort_order="asc",
        skip=0,
        limit=10,
    )

    assert total >= 3
    titles = [r[0].title for r in rows[:3]]
    assert set(["A Plan", "B Plan", "C Plan"]) <= set(titles)

    # Search filter
    rows, total = get_plans(
        db=db,
        search="A",
        sort_by="status",
        sort_order="asc",
        skip=0,
        limit=10,
    )
    assert any(r[0].title == "A Plan" for r in rows)
    assert all("A" in r[0].title for r in rows)

    # Pagination
    rows, total = get_plans(
        db=db,
        search=None,
        sort_by="status",
        sort_order="asc",
        skip=1,
        limit=1,
    )
    assert len(rows) == 1
    assert rows[0][0].title in ["A Plan", "B Plan", "C Plan"]


def test_get_plans_sort_by_total_days_desc(db):
    author = _create_author(db)

    # Create three plans and attach different numbers of items
    plan_counts = {"Zero": 0, "One": 1, "Two": 2}
    created = {}
    for title, count in plan_counts.items():
        p = Plan(
            title=f"{title} Items Plan",
            description="desc",
            author_id=author.id,
            created_by="tester",
        )
        p = save_plan(db, p)
        created[title] = p
        for day in range(count):
            item = PlanItem(
                plan_id=p.id,
                day_number=day + 1,
                created_by="tester",
            )
            db.add(item)
        db.commit()

    rows, total = get_plans(
        db=db,
        search=None,
        sort_by="total_days",
        sort_order="desc",
        skip=0,
        limit=10,
    )

    # Extract just the seeded three for assertion order
    titles_in_order = [r[0].title for r in rows if r[0].title.endswith("Items Plan")]
    # Expect Two > One > Zero by total_days
    assert titles_in_order[:3] == [
        "Two Items Plan",
        "One Items Plan",
        "Zero Items Plan",
    ]


