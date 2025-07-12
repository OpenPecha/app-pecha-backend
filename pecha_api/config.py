import os

DEFAULTS = dict(
    ACCESS_TOKEN_EXPIRE_MINUTES=30,
    APP_NAME="Pecha Backend",
    AWS_ACCESS_KEY="",
    AWS_SECRET_KEY="",
    AWS_REGION="eu-central-1",
    AWS_BUCKET_NAME="app-pecha-backend",
    BASE_URL="https://pech.org",
    CLIENT_ID="",
    COMPRESSED_QUALITY=80,
    DATABASE_URL="postgresql://admin:pechaAdmin@localhost:5434/pecha",
    DEFAULT_LANGUAGE="en",
    DEFAULT_PAGE_SIZE=10,
    DEPLOYMENT_MODE="DEBUG",
    DOMAIN_NAME="dev-pecha-esukhai.us.auth0.com",
    IMAGE_EXPIRATION_IN_SEC=3600,
    JWT_ALGORITHM="HS256",
    JWT_AUD="https://pecha.org",
    JWT_ISSUER="https://pecha.org",
    JWT_SECRET_KEY="",
    MAX_FILE_SIZE_MB=1,

    MONGO_CONNECTION_STRING="mongodb://admin:pechaAdmin@localhost:27017/pecha?authSource=admin",

    MONGO_DATABASE_NAME="pecha",
    REFRESH_TOKEN_EXPIRE_DAYS=30,
    SENDGRID_API_KEY="",
    SENDGRID_SENDER_EMAIL="",
    VERSION="0.0.1",
    # Cache Configuration
    CACHE_HOST="localhost",
    CACHE_PORT=6379,
    CACHE_DB=0,
    CACHE_PREFIX="pecha:",
    CACHE_DEFAULT_TIMEOUT=60, # 1 minute in seconds

    SHORT_URL_GENERATION_ENDPOINT="https://url-shortening-14682653622-b69c6fd.onrender.com/api/v1",
    PECHA_BACKEND_ENDPOINT="https://pecha-backend-12341825340-1fb0112.onrender.com/api/v1",

    # Search configuration
    ELASTICSEARCH_URL= None,
    ELASTICSEARCH_API=None,
    ELASTICSEARCH_CONTENT_INDEX = "pecha-texts",
    ELASTICSEARCH_SEGMENT_INDEX = "pecha-segments",
    ELASTICSEARCH_SHEET_INDEX = "pecha-sheets"
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


def get_int(key: str) -> int:
    try:
        return int(get(key))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Could not convert the value for key '{key}' to int: {e}")
