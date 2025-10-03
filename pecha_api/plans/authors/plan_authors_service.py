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
from pecha_api.plans.authors.plan_authors_model import Author, AuthorSocialMediaAccount
from pecha_api.plans.authors.plan_authors_repository import get_author_by_email, get_author_by_id, get_all_authors, \
    update_author
import jose

from pecha_api.plans.authors.plan_authors_response_models import AuthorInfoResponse, SocialMediaProfile, \
    AuthorsResponse, AuthorInfoRequest
from pecha_api.plans.plans_response_models import PlansResponse
from pecha_api.plans.shared.utils import load_plans_from_json
from pecha_api.uploads.S3_utils import generate_presigned_access_url
from pecha_api.users.users_service import get_social_profile
from pecha_api.plans.public.plan_service import convert_plan_model_to_dto
from pecha_api.utils import Utils


async def get_authors() -> AuthorsResponse:
    with SessionLocal() as db_session:
        authors = get_all_authors(db=db_session)
        authors_response = [AuthorInfoResponse(
            id=author.id,
            firstname=author.first_name,
            lastname=author.last_name,
            email=author.email,
            avatar_url=generate_presigned_access_url(bucket_name=get("AWS_BUCKET_NAME"), s3_key= author.image_url),
            bio=author.bio,
            social_profiles=_get_author_social_profile(author=author)
        ) for author in authors]
        return AuthorsResponse(
            authors=authors_response,
            skip=0,
            limit=20,
            total=len(authors)
        )

async def get_author_details(token: str) -> AuthorInfoResponse:
    author = await validate_and_extract_author_details(token=token)
    social_media_profiles = _get_author_social_profile(author=author)
    return AuthorInfoResponse(
        id=author.id,
        firstname=author.first_name,
        lastname=author.last_name,
        email=author.email,
        avatar_url=generate_presigned_access_url(bucket_name=get("AWS_BUCKET_NAME"), s3_key= author.image_url),
        bio=author.bio,
        social_profiles=social_media_profiles
    )

def update_social_profiles(author: Author, social_profiles: List[SocialMediaProfile]) -> None:
    existing_profiles = {profile.platform_name: profile for profile in author.social_media_accounts}

    for profile_data in social_profiles or []:
        platform = profile_data.account.name
        url = profile_data.url

        if platform in existing_profiles:
            # Update existing profile
            existing_profiles[platform].profile_url = url
        else:
            # Add new profile
            author.social_media_accounts.append(AuthorSocialMediaAccount(
                author_id=author.id,
                platform_name=platform,
                profile_url=url
            ))

async def update_author_info(token: str, author_info_request: AuthorInfoRequest) -> Author:
    current_author = await validate_and_extract_author_details(token=token)
    current_author.first_name = author_info_request.firstname
    current_author.last_name = author_info_request.lastname
    current_author.bio = author_info_request.bio
    current_author.image_url = Utils.extract_s3_key(presigned_url=author_info_request.avatar_url)
    with SessionLocal() as db_session:
        try:
            db_session.add(current_author)
            update_social_profiles(author=current_author, social_profiles=author_info_request.social_profiles)
            updated_user = update_author(db=db_session, author=current_author)
            return updated_user
        except Exception as e:
            db_session.rollback()
            logging.error(f"Failed to update user info: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_selected_author_details(author_id: UUID) -> AuthorInfoResponse:
    author = await _get_author_details_by_id(author_id=author_id)
    social_media_profiles = _get_author_social_profile(author=author)
    return AuthorInfoResponse(
        id=author.id,
        firstname=author.first_name,
        lastname=author.last_name,
        email=author.email,
        avatar_url=generate_presigned_access_url(bucket_name=get("AWS_BUCKET_NAME"), s3_key= author.image_url),
        bio=author.bio,
        social_profiles=social_media_profiles
    )

async def get_plans_by_author(author_id: UUID,skip: int = 0, limit: int = 20) -> PlansResponse:
    await _get_author_details_by_id(author_id=author_id)
    # Load plans from JSON file
    plan_listing = load_plans_from_json()
    # Filter published plans by author_id and convert to DTOs
    published_plans = [
        convert_plan_model_to_dto(p) 
        for p in plan_listing.plans 
        if p.status == "PUBLISHED" and p.author and p.author.id == str(author_id)
    ]
     # Apply pagination
    total = len(published_plans)
    paginated_plans = published_plans[skip:skip + limit]
    
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

async def validate_and_extract_author_details(token: str) -> Author:
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