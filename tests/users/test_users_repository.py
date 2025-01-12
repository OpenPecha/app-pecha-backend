import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette import status

from pecha_api.auth.auth_enums import RegistrationSource
from pecha_api.users.users_models import Base, Users, SocialMediaAccount
from pecha_api.users.users_repository import save_user, get_user_by_email, get_user_by_username, get_user_social_account

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


def test_get_user_by_username(db):
    user = Users(
        email="testuser3@example.com",
        username="testuser3",
        firstname='firstname',
        lastname='lastname',
        password='password',
        registration_source=RegistrationSource.EMAIL.name
    )
    save_user(db, user)
    fetched_user = get_user_by_username(db, "testuser3")
    assert fetched_user is not None
    assert fetched_user.username == "testuser3"


def test_get_user_social_account(db):
    user = Users(
        email="testuser4@example.com",
        username="testuser4",
        firstname='firstname',
        lastname='lastname',
        password='password',
        registration_source=RegistrationSource.EMAIL.name
    )
    saved_user = save_user(db, user)
    social_account = SocialMediaAccount(
        user_id=saved_user.id,
        platform_name="linkedin",
        profile_url="http://linkedin.com/in/johndoe"
    )
    db.add(social_account)
    db.commit()
    fetched_social_accounts = get_user_social_account(db, saved_user.id)
    assert fetched_social_accounts is not None
    assert fetched_social_accounts.count() == 1
    assert fetched_social_accounts.first().platform_name == "linkedin"
    assert fetched_social_accounts.first().profile_url == "http://linkedin.com/in/johndoe"


def test_get_user_by_email_not_found(db):
    with pytest.raises(HTTPException) as exc_info:
        get_user_by_email(db, "nonexistent@example.com")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found"
