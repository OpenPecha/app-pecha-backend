from fastapi import APIRouter,Header,Depends
from starlette import status
from ..db import database
from fastapi import HTTPException
from typing import Annotated
user_router = APIRouter(
    prefix="/users",
    tags=["User Profile"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_token_from_header(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    return authorization.split(" ")[1]

@user_router.get("/info", status_code=status.HTTP_200_OK)
def get_user_info(token: Annotated[str, Depends(get_token_from_header)]):
    return "User Info"