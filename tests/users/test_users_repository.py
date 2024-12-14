import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pecha_api.auth.auth_enums import RegistrationSource
from pecha_api.users.users_models import Base, Users
from pecha_api.users.user_repository import save_user, get_user_by_email

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_save_user(db):
    user = Users(
        email="testuser@example.com",
        firstname='firstname',
        lastname='lastname',
        password='password',
        registration_source=RegistrationSource.EMAIL.name
    )
    saved_user = save_user(db, user)
    assert saved_user.id is not None
    assert saved_user.email == "testuser@example.com"


def test_get_user_by_email(db):
    user = Users(
        email="testuser2@example.com",
        firstname='firstname',
        lastname='lastname',
        password='password',
        registration_source=RegistrationSource.EMAIL.name
    )
    save_user(db, user)
    fetched_user = get_user_by_email(db, "testuser2@example.com")
    assert fetched_user is not None
    assert fetched_user.email == "testuser2@example.com"
