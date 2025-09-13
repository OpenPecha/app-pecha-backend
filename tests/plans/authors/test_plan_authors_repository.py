from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from pecha_api.plans.authors.plan_authors_repository import (
    save_author,
    get_author_by_email,
    get_author_by_id,
    update_author,
    check_author_exists,
)
from fastapi import HTTPException
from pecha_api.plans.response_message import AUTHOR_NOT_FOUND, AUTHOR_UPDATE_INVALID, AUTHOR_ALREADY_EXISTS, BAD_REQUEST


def _make_session_mock() -> Session:
    return MagicMock(spec=Session)


def test_save_author_success_commits_and_returns_author():
    db = _make_session_mock()
    author = MagicMock(name="AuthorInstance")

    result = save_author(db=db, author=author)

    assert result is author
    db.add.assert_called_once_with(author)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(author)


def test_save_author_integrity_error_raises_404_and_rolls_back():
    db = _make_session_mock()
    author = MagicMock(name="AuthorInstance")
    db.commit.side_effect = IntegrityError(None, None, Exception("duplicate email"))

    with pytest.raises(HTTPException) as exc:
        save_author(db=db, author=author)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "duplicate email"
    db.rollback.assert_called_once()


def test_get_author_by_email_returns_author_when_found():
    db = _make_session_mock()
    expected_author = MagicMock(name="AuthorInstance")
    db.query.return_value.filter.return_value.first.return_value = expected_author

    result = get_author_by_email(db=db, email="john.doe@example.com")

    assert result is expected_author
    db.query.assert_called_once()
    db.query.return_value.filter.assert_called_once()


def test_get_author_by_email_not_found_raises_404():
    db = _make_session_mock()
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        get_author_by_email(db=db, email="missing@example.com")

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == AUTHOR_NOT_FOUND


def test_get_author_by_id_returns_author_when_found():
    db = _make_session_mock()
    expected_author = MagicMock(name="AuthorInstance")
    db.query.return_value.filter.return_value.first.return_value = expected_author

    result = get_author_by_id(db=db, author_id="123e4567-e89b-12d3-a456-426614174000")

    assert result is expected_author
    db.query.assert_called_once()
    db.query.return_value.filter.assert_called_once()


def test_get_author_by_id_not_found_raises_404():
    db = _make_session_mock()
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        get_author_by_id(db=db, author_id="123e4567-e89b-12d3-a456-426614174999")

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == AUTHOR_NOT_FOUND


def test_update_author_success_commits_and_returns_author():
    db = _make_session_mock()
    author = MagicMock(name="AuthorInstance")

    result = update_author(db=db, author=author)

    assert result is author
    db.add.assert_called_once_with(author)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(author)


def test_update_author_integrity_error_raises_400_and_rolls_back():
    db = _make_session_mock()
    author = MagicMock(name="AuthorInstance")
    db.commit.side_effect = IntegrityError(None, None, Exception("some constraint"))

    with pytest.raises(HTTPException) as exc:
        update_author(db=db, author=author)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == AUTHOR_UPDATE_INVALID
    db.rollback.assert_called_once()



def test_check_author_exists_raises_400_when_author_exists():
    db = _make_session_mock()
    db.query.return_value.filter.return_value.first.return_value = MagicMock(name="AuthorInstance")

    with pytest.raises(HTTPException) as exc:
        check_author_exists(db=db, email="exists@example.com")

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == {"error": BAD_REQUEST, "message": AUTHOR_ALREADY_EXISTS}


def test_check_author_exists_no_exception_when_author_not_exists():
    db = _make_session_mock()
    db.query.return_value.filter.return_value.first.return_value = None

    # Should not raise
    result = check_author_exists(db=db, email="new@example.com")
    assert result is None

