import logging
from ..config import get
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi import HTTPException
from starlette import status


def send_email(to_email: str, subject: str, message: str):
    message = Mail(
        from_email=get('SENDGRID_SENDER_EMAIL'),
        to_emails=to_email,
        subject=subject,
        html_content=message
    )
    try:
        sg = SendGridAPIClient(get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email send failed.")
