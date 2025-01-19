import os

DEFAULTS = dict(
    ACCESS_TOKEN_EXPIRE_MINUTES=30,
    APP_NAME="Pecha Backend",
    AWS_ACCESS_KEY="",
    AWS_SECRET_KEY="",
    AWS_REGION="eu-central-1",
    AWS_BUCKET_NAME="app-pecha-backend",
    BASE_URL="https://pech.org",
    COMPRESSED_QUALITY= 80,
    IMAGE_EXPIRATION_IN_SEC=3600,
    DEPLOYMENT_MODE="DEBUG",
    DATABASE_URL="postgresql://admin:pechaAdmin@localhost:5434/pecha",
    JWT_ALGORITHM="HS256",
    JWT_AUD="https://pecha.org",
    JWT_ISSUER="https://pecha.org",
    JWT_SECRET_KEY="oJvUxI5jY7nXaD4sC_kFGoM0_qAuewVxg3p6F8CH-tI",
    MAX_FILE_SIZE_MB = 1,
    REFRESH_TOKEN_EXPIRE_DAYS=30,
    SENDGRID_API_KEY="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",
    SENDGRID_SENDER_EMAIL="samten@esukhia.org",
    VERSION="0.0.1"
)


def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return DEFAULTS[key]


def get_float(key: str) -> float:
    try:
        return float(get(key))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Could not convert the value for key '{key}' to float: {e}")

def get_int(key: str) -> float:
    try:
        return int(get(key))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Could not convert the value for key '{key}' to float: {e}")
