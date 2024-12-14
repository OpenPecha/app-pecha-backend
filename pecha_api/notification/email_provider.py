import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_message(to_email: str, subject: str, message: str):
    message = Mail(
        from_email=os.environ.get('SENDGRID_SENDER_EMAIL'),
        to_emails=to_email,
        subject=subject,
        html_content=message
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        logging.error(e.message)
