from .plan_auth_model import CreateAuthorRequest, AuthorResponse, AuthorDetails
from pecha_api.plans.plan_models import Author
from pecha_api.db.database import SessionLocal
from pecha_api.plans.authors.plan_authors import save_author, get_author_by_email, update_author
from pecha_api.auth.auth_repository import get_hashed_password
from fastapi import HTTPException
from starlette import status
from datetime import datetime, timedelta, timezone
from jose import jwt
from pecha_api.config import get
from pecha_api.notification.email_provider import send_email
from pecha_api.auth.auth_repository import get_hashed_password, verify_password, create_access_token, create_refresh_token, \
    generate_token_data
from pecha_api.plans.plan_auth.plan_auth_model import AuthorLoginResponse
from plan_auth_model import TokenResponse, AuthorInfo


def register_author(create_user_request: CreateAuthorRequest) -> AuthorResponse:
    registered_user = _create_user(
        create_user_request=create_user_request
    )
    return AuthorResponse(author=registered_user)

def _create_user(create_user_request: CreateAuthorRequest) -> AuthorDetails:
    new_author = Author(**create_user_request.model_dump())
    _validate_password(new_author.password)
    hashed_password = get_hashed_password(new_author.password)
    new_author.password = hashed_password
    with SessionLocal() as db_session:
        saved_author = save_author(db=db_session, author=new_author)
    _send_verification_email(email=saved_author.email)
    return AuthorDetails(
        id=saved_author.id,
        first_name=saved_author.first_name,
        last_name=saved_author.last_name,
        email=saved_author.email,
        created_at=saved_author.created_at,
        updated_at=saved_author.updated_at
    )

def _validate_password(password: str):
    if not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be empty")
    if len(password) < 8 or len(password) > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password must be between 8 and 20 characters")


def _generate_author_verification_token(email: str) -> str:
    expires_delta = timedelta(hours=24)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "email": email,
        "iss": get("JWT_ISSUER"),
        "aud": get("JWT_AUD"),
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "typ": "author_email_verification"
    }
    return jwt.encode(payload, get("JWT_SECRET_KEY"), algorithm=get("JWT_ALGORITHM"))


def _send_verification_email(email: str) -> None:
    token = _generate_author_verification_token(email=email)
    backend_endpoint = get("PECHA_BACKEND_ENDPOINT")
    verify_link = f"{backend_endpoint}/plan-auth/verify-email?token={token}"

    html_content = f"""
        <div>
            <p>Welcome to Pecha!</p>
            <p>Please verify your email address by clicking the link below:</p>
            <p><a href=\"{verify_link}\">Verify Email</a></p>
            <p>This link expires in 24 hours.</p>
        </div>
    """
    send_email(
        to_email=email,
        subject="Verify your Pecha account",
        message=html_content
    )


def verify_author_email(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            get("JWT_SECRET_KEY"),
            algorithms=[get("JWT_ALGORITHM")],
            audience=get("JWT_AUD")
        )
        if payload.get("typ") != "author_email_verification":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type")
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload")
        with SessionLocal() as db_session:
            author = get_author_by_email(db=db_session, email=email) # need validation for author
            if author.is_verified:
                return {"message": "Email already verified"}
            author.is_verified = True
            update_author(db=db_session, author=author)
            return {"message": "Email verified successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")


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
                detail='Invalid email or password'
            )
        return author

def check_verified_author(author: Author) -> bool:
    if not author.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Author not verified')
    elif not author.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Author not active')    
    

def authenticate_and_generate_tokens(email: str, password: str):
    author = authenticate_author(email=email, password=password)
    return generate_token_author(author)

def generate_token_author(author: Author):
    data = generate_token_data(author)
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)

    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer"
    )
    return AuthorLoginResponse(
        user=AuthorInfo(
            name=author.firstname + " " + author.lastname,
            avatar_url=author.avatar_url
        ),
        auth=token_response
    )
