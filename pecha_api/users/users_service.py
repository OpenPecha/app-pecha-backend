from fastapi import HTTPException, status
from starlette.responses import JSONResponse

from .user_response_models import UserInfoResponse
from ..auth.auth_repository import decode_token
from .users_repository import get_user_by_email
from ..db.database import SessionLocal


def get_user_info(token: str):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        db_session = SessionLocal()
        user = get_user_by_email(db=db_session, email=email)
        user_info_response = UserInfoResponse(
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            followes=0,
            following=0,
            avater_url=""
        )
        return user_info_response
    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})
