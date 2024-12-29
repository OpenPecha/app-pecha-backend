from fastapi import HTTPException, status
from ..auth.auth_repository import decode_token
from .users_repository import get_user_by_email
def get_user_info(token: str):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = get_user_by_email(email=email)
        return user
    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})
    
