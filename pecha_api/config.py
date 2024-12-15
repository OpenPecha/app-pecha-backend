import os

DEFAULTS = dict(
    ACCESS_TOKEN_EXPIRE_MINUTES=30,
    APP_NAME="Pecha Backend",
    BASE_URL="https://pech.org",
    DEPLOYMENT_MODE="DEBUG",
    JWT_ALGORITHM="HS256",
    JWT_AUD="https://pecha.org",
    JWT_ISSUER="https://pecha.org",
    JWT_SECRET_KEY="oJvUxI5jY7nXaD4sC_kFGoM0_qAuewVxg3p6F8CH-tI",
    REFRESH_TOKEN_EXPIRE_DAYS=30,
    SENDGRID_API_KEY="",
    SENDGRID_SENDER_EMAIL="",
    VERSION="0.0.1"

)


def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return DEFAULTS[key]


def get_float(key: str) -> float:
    return float(get(key))
