from fastapi import FastAPI
from starlette import status
from fastapi.middleware.cors import CORSMiddleware

from auth.auth_models import PropsResponse
from pecha_api.auth import auth_views
from pecha_api.users import users_views
import uvicorn
from config import get

api = FastAPI(
    title="Pecha API",
    description="This is the API documentation for Pecha application",
    root_path="/api/v1",
    redoc_url="/docs"
)
api.include_router(auth_views.auth_router)
api.include_router(users_views.user_router)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/props", status_code=status.HTTP_204_NO_CONTENT)
async def get_props():
    props_response = PropsResponse(
        client_id=get("CLIENT_ID"),
        domain=get("DOMAIN_NAME")
    )
    return props_response

@api.get("/health", status_code=status.HTTP_204_NO_CONTENT)
async def get_health():
    return {'status': 'up'}

if __name__ == "__main__":
    uvicorn.run("pecha_api.app:api", host="127.0.0.1", port=8000, reload=True)

