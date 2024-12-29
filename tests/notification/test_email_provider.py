from unittest.mock import patch, Mock
from pecha_api.notification.email_provider import send_email
from fastapi import HTTPException
import pytest


def test_send_email_success():
    with patch('pecha_api.notification.email_provider.SendGridAPIClient') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.send.return_value = Mock(status_code=202)

        send_email('test@example.com', 'Test Subject', 'Test Message')

        mock_instance.send.assert_called_once()


def test_send_email_failure():
    with patch('pecha_api.notification.email_provider.SendGridAPIClient') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.send.side_effect = Exception("Send failed")

        with pytest.raises(HTTPException) as exc_info:
            send_email('test@example.com', 'Test Subject', 'Test Message')

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Email send failed."
