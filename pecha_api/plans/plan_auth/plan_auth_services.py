from .plan_auth_model import CreateAuthorRequest, AuthorResponse, AuthorDetails
from pecha_api.plans.plan_models import Author
from pecha_api.db.database import SessionLocal
from pecha_api.plans.authors.plan_authors import save_author
from pecha_api.auth.auth_service import get_hashed_password
from fastapi import HTTPException
from starlette import status

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
