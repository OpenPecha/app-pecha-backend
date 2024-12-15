from sqlalchemy.orm import Session
from pecha_api.auth.password_reset_repository import save_password_reset, get_password_reset_by_token
from pecha_api.users.users_models import PasswordReset
import pytest
from unittest.mock import MagicMock


def test_save_password_reset():
    db = MagicMock(spec=Session)
    password_reset = PasswordReset(
        email="test@example.com",
        reset_token="test_token")

    result = save_password_reset(db, password_reset)

    db.add.assert_called_once_with(password_reset)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(password_reset)
    assert result == password_reset


def test_get_password_reset_by_token():
    db = MagicMock(spec=Session)
    token = "test_token"
    expected_password_reset = PasswordReset(reset_token=token)
    db.query().filter().first.return_value = expected_password_reset

    result = get_password_reset_by_token(db, token)
    assert result == expected_password_reset
