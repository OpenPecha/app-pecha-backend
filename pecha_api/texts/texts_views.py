from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status

from .texts_service import get_text_by_term

oauth2_scheme = HTTPBearer()
text_router = APIRouter(
    prefix="/texts",
    tags=["Texts"]
)


@text_router.get("", status_code=status.HTTP_200_OK)
def get_text(language: str | None):
    return get_text_by_term(language=language)
