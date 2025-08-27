from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...db import database
from .plan_auth_enums import RegistrationSource
from .plan_auht_model import CreateAuthorRequest

plan_auth_router = APIRouter(
    prefix="/plan-auth",
    tags=["Plan Authentications"],
)
