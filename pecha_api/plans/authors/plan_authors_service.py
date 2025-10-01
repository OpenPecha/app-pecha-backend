import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException
from jose import JWTError
from jose.exceptions import JWTClaimsError
from jwt import ExpiredSignatureError
from starlette import status

from pecha_api.config import get
from pecha_api.auth.auth_repository import validate_token
from pecha_api.db.database import SessionLocal
from pecha_api.error_contants import ErrorConstants
from pecha_api.plans.authors.plan_authors_model import Author
from pecha_api.plans.authors.plan_authors_repository import get_author_by_email, get_author_by_id
import jose

from pecha_api.plans.authors.plan_authors_response_models import AuthorInfoResponse, SocialMediaProfile
from pecha_api.plans.plans_response_models import PlansResponse
from pecha_api.plans.shared.utils import load_plans_from_json
from pecha_api.uploads.S3_utils import generate_presigned_access_url
from pecha_api.users.users_enums import SocialProfile
from pecha_api.users.users_service import get_social_profile


def validate_and_extract_author_details(token: str) -> Author:
    try:
        payload = validate_token(token)
        email = payload.get("email")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
        with SessionLocal() as db_session:
            author = get_author_by_email(db=db_session, email=email)
            return author
    except ExpiredSignatureError as exception:
        logging.debug(f"exception: {exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except jose.ExpiredSignatureError as exception:
        logging.debug(f"exception: {exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except JWTClaimsError as exception:
        logging.debug(f"exception: {exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except ValueError as value_exception:
        logging.debug(f"exception: {value_exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except JWTError as jwt_exception:
        logging.debug(f"exception: {jwt_exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)


async def get_selected_author_details(author_id: UUID) -> AuthorInfoResponse:
    author = await _get_author_details_by_id(author_id=author_id)
    social_media_profiles = _get_author_social_profile(author=author)
    return AuthorInfoResponse(
        firstname=author.firstname,
        lastname=author.lastname,
        email=author.email,
        avatar_url=generate_presigned_access_url(bucket_name=get("AWS_BUCKET_NAME"), s3_key= author.image_url),
        bio=author.bio,
        social_profiles=social_media_profiles
    )

async def get_plans_by_author(author_id: UUID,skip: int = 0,
    limit: int = 20) -> PlansResponse:
    await _get_author_details_by_id(author_id=author_id)
    # Load plans from JSON file
    plan_listing = load_plans_from_json()
     # Apply pagination
    total = len(plan_listing)
    paginated_plans = plan_listing[skip:skip + limit]
    
    return PlansResponse(
        plans=paginated_plans,
        skip=skip,
        limit=limit,
        total=total
    )
async def _get_author_details_by_id(author_id: UUID) -> Author:
    with SessionLocal() as db_session:
        author = get_author_by_id(db=db_session,author_id=author_id)
        return author

def _get_author_social_profile(author: Author) -> List[SocialMediaProfile]:
    social_media_profiles = []
    for account in author.social_media_accounts:
        social_media_profile = SocialMediaProfile(
            account=get_social_profile(value=account.platform_name),
            url=account.profile_url
        )
        social_media_profiles.append(social_media_profile)
    return social_media_profiles