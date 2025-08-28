from .plan_auth_model import CreateAuthorRequest
from pecha_api.plans.plan_models import Author
from pecha_api.db.database import SessionLocal
from pecha_api.plans.authors.plan_authors import save_user

def register_author(create_user_request: CreateAuthorRequest):
    registered_user = create_user(
        create_user_request=create_user_request
    )
    return registered_user

def create_user(create_user_request: CreateAuthorRequest):
    new_user = Author(**create_user_request.model_dump())
    with SessionLocal() as db_session:
        saved_user = save_user(db=db_session, user=new_user)
        return saved_user
