import os
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette import status

from pecha_api.auth.auth_enums import RegistrationSource
from pecha_api.users.users_models import Base, Users, SocialMediaAccount, PasswordReset
from pecha_api.users.users_repository import save_user, get_user_by_email, get_user_by_username, \
    get_user_social_account, update_user

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
    # Create only the users-related tables to avoid touching unrelated metadata
    Base.metadata.create_all(
        bind=engine,
        tables=[Users.__table__, SocialMediaAccount.__table__, PasswordReset.__table__],
    )
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(
        bind=engine,
        tables=[Users.__table__, SocialMediaAccount.__table__, PasswordReset.__table__],
    )


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


def test_save_user_integrity_error(db):
    user1 = Users(
        email="duplicate@example.com",
        username="user1",
        firstname='firstname',
        lastname='lastname',
        password='password',
        registration_source=RegistrationSource.EMAIL.name
    )
    user2 = Users(
        email="duplicate@example.com",  # Duplicate email should cause an integrity error
        username="user2",
        firstname='firstname',
        lastname='lastname',
        password='password',
        registration_source=RegistrationSource.EMAIL.name
    )
    save_user(db, user1)
    with pytest.raises(HTTPException) as exc_info:
        save_user(db, user2)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found"


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


def test_update_user(db):
    user = Users(
        email="testuser5@example.com",
        username="testuser5",
        firstname='firstname',
        lastname='lastname',
        password='password',
        registration_source=RegistrationSource.EMAIL.name
    )
    saved_user = save_user(db, user)
    saved_user.firstname = "updated_firstname"
    updated_user = update_user(db, saved_user)
    assert updated_user.firstname == "updated_firstname"


def test_update_user_invalid_request(db):
    user = Users(
        email="testuser6@example.com",
        username="testuser6",
        firstname='firstname',
        lastname='lastname',
        password='password',
        registration_source=RegistrationSource.EMAIL.name
    )
    save_user(db, user)
    user.id = None  # Invalid update request
    with pytest.raises(HTTPException) as exc_info:
        update_user(db, user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "User update issue"


def test_update_user_integrity_error(db):
    user1 = Users(
        email="testuser7@example.com",
        username="testuser7",
        firstname='firstname',
        lastname='lastname',
        password='password',
        registration_source=RegistrationSource.EMAIL.name
    )
    user2 = Users(
        email="testuser8@example.com",
        username="testuser8",
        firstname='firstname',
        lastname='lastname',
        password='password',
        registration_source=RegistrationSource.EMAIL.name
    )
    save_user(db, user1)
    save_user(db, user2)
    user2.email = "testuser7@example.com"  # This should cause an integrity error
    with pytest.raises(HTTPException) as exc_info:
        update_user(db, user2)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "User update issue"
