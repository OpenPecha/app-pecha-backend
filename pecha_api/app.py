from fastapi import FastAPI
from starlette import status
from fastapi.middleware.cors import CORSMiddleware

from pecha_api.db.mongo_database import lifespan
from pecha_api.auth import auth_views
from pecha_api.users import users_views
import uvicorn

api = FastAPI(
    title="Pecha API",
    description="This is the API documentation for Pecha application",
    root_path="/api/v1",
    redoc_url="/docs",
    lifespan=lifespan
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



@api.get("/health", status_code=status.HTTP_204_NO_CONTENT)
async def get_health():
    return {'status': 'up'}

if __name__ == "__main__":
    uvicorn.run("pecha_api.app:api", host="127.0.0.1", port=8000, reload=True)

