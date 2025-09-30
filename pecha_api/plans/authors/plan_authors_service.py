import logging
from uuid import UUID

from fastapi import HTTPException
from jose import JWTError
from jose.exceptions import JWTClaimsError
from jwt import ExpiredSignatureError
from pydantic.v1 import UUID1
from starlette import status

from pecha_api.auth.auth_repository import validate_token
from pecha_api.db.database import SessionLocal
from pecha_api.error_contants import ErrorConstants
from pecha_api.plans.authors.plan_authors_model import Author
from pecha_api.plans.authors.plan_authors_repository import get_author_by_email, get_author_by_id
import jose

from plans.authors.plan_authors_response_models import AuthorInfoResponse


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
    with SessionLocal() as db_session:
        selected_author = get_author_by_id(db=db_session,author_id=author_id)
        return  AuthorInfoResponse(
            firstname=selected_author.first_name,
            lastname=selected_author.last_name,
            email=selected_author.email,
            avatar_url=selected_author.image_url,
            bio=selected_author.bio
        )