from .plan_auth_enums import AuthorStatus
from .plan_auth_models import CreateAuthorRequest, AuthorResponse, AuthorDetails, TokenPayload, \
    AuthorVerificationResponse
from pecha_api.plans.authors.plan_author_model import Author
from pecha_api.db.database import SessionLocal
from pecha_api.plans.authors.plan_authors_repository import save_author, get_author_by_email, update_author
from pecha_api.auth.auth_repository import get_hashed_password
from fastapi import HTTPException
from starlette import status
from datetime import datetime, timedelta, timezone
from jose import jwt
from pecha_api.config import get
from pecha_api.notification.email_provider import send_email
from jinja2 import Template
from pathlib import Path
from pecha_api.plans.response_message import (
    PASSWORD_EMPTY,
    PASSWORD_LENGTH_INVALID,
    TOKEN_EXPIRED,
    TOKEN_INVALID,
    EMAIL_VERIFIED_SUCCESS, 
    EMAIL_ALREADY_VERIFIED,
    REGISTRATION_MESSAGE,
    AUTHOR_NOT_VERIFIED,
    AUTHOR_NOT_ACTIVE,
    INVALID_EMAIL_PASSWORD
)

from pecha_api.auth.auth_repository import get_hashed_password

from pecha_api.auth.auth_repository import get_hashed_password, verify_password, create_access_token, create_refresh_token
from .plan_auth_models import TokenResponse, AuthorLoginResponse, AuthorInfo

def register_author(create_user_request: CreateAuthorRequest) -> AuthorDetails:
    registered_user = _create_user(
        create_user_request=create_user_request
    )
    return registered_user

def _create_user(create_user_request: CreateAuthorRequest) -> AuthorDetails:
    new_author = Author(**create_user_request.model_dump())
    new_author.created_by = create_user_request.email
    _validate_password(new_author.password)
    hashed_password = get_hashed_password(new_author.password)
    new_author.password = hashed_password
    with SessionLocal() as db_session:
        saved_author = save_author(db=db_session, author=new_author)
    _send_verification_email(email=saved_author.email)
    return AuthorDetails(
        first_name=saved_author.first_name,
        last_name=saved_author.last_name,
        email=saved_author.email,
        status=AuthorStatus.PENDING_VERIFICATION,
        message=REGISTRATION_MESSAGE
    )

def _validate_password(password: str):
    if not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_EMPTY)
    if len(password) < 8 or len(password) > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_LENGTH_INVALID)


def _generate_author_verification_token(email: str) -> str:
    expires_delta = timedelta(hours=24)
    expire = datetime.now(timezone.utc) + expires_delta

    payload = TokenPayload(
        email=email,
        iss=get("JWT_ISSUER"),
        aud=get("JWT_AUD"),
        iat=datetime.now(timezone.utc),
        exp=expire,
        typ="author_email_verification"
    )
    return jwt.encode(payload.model_dump(), get("JWT_SECRET_KEY"), algorithm=get("JWT_ALGORITHM"))


def _send_verification_email(email: str) -> None:
    token = _generate_author_verification_token(email=email)
    frontend_endpoint = get("BASE_URL")
    verify_link = f"{frontend_endpoint}/plan/verify-email?token={token}"

    template_path = Path(__file__).parent / "templates" / "verify_email_template.html"
    with open(template_path, "r") as f:
        template = Template(f.read())
    html_content = template.render(verify_link=verify_link)
    send_email(
        to_email=email,
        subject="Verify your Pecha account",
        message=html_content
    )


def verify_author_email(token: str) -> AuthorVerificationResponse:
    try:
        payload = jwt.decode(
            token,
            get("JWT_SECRET_KEY"),
            algorithms=[get("JWT_ALGORITHM")],
            audience=get("JWT_AUD")
        )
        if payload.get("typ") != "author_email_verification":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=TOKEN_INVALID)
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=TOKEN_INVALID)
        with SessionLocal() as db_session:
            author = get_author_by_email(db=db_session, email=email) # need validation for author
            if not author.is_verified:
                author.is_verified = True
                update_author(db=db_session, author=author)
                message = EMAIL_VERIFIED_SUCCESS
            else:
                message = EMAIL_ALREADY_VERIFIED
            return AuthorVerificationResponse(
                email=author.email,
                status=AuthorStatus.INACTIVE,
                message=message
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=TOKEN_EXPIRED)
    except HTTPException as e:
        # Re-raise expected HTTP errors (type/payload validation) without masking
        raise e
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=TOKEN_INVALID)


def authenticate_author(email: str, password: str):
    with SessionLocal() as db_session:
        author = get_author_by_email(db=db_session, email=email)
        check_verified_author(author=author)
        if not verify_password(
                plain_password=password,
                hashed_password=author.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_EMAIL_PASSWORD
            )
        return author

def check_verified_author(author: Author) -> bool:
    if not author.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = AUTHOR_NOT_VERIFIED)
    elif not author.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = AUTHOR_NOT_ACTIVE)    
    

def authenticate_and_generate_tokens(email: str, password: str):
    author = authenticate_author(email=email, password=password)
    return generate_token_author(author)

def generate_author_token_data(author: Author):
    if not all([author.email, author.first_name, author.last_name]):
        return None
    data = {
        "email": author.email,
        "name": author.first_name + " " + author.last_name,
        "iss": get("JWT_ISSUER"),
        "aud": get("JWT_AUD"),
        "iat": datetime.now(timezone.utc)
    }
    return data

def generate_token_author(author: Author):
    data = generate_author_token_data(author)
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)

    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer"
    )
    return AuthorLoginResponse(
        user=AuthorInfo(
            name=author.first_name + " " + author.last_name,
            image_url=author.image_url
        ),
        auth=token_response
    )
