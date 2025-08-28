from .plan_auth_model import CreateAuthorRequest
from pecha_api.plans.plan_models import Author

def register_author(create_user_request: CreateAuthorRequest):
    registered_user = create_user(
        create_user_request=create_user_request
    )
    return registered_user

def create_user(create_user_request: CreateAuthorRequest):
    new_user = Author(**create_user_request.model_dump())
    return new_user