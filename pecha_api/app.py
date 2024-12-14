from fastapi import FastAPI
from starlette import status
from pecha_api.auth import auth_views
import uvicorn

api = FastAPI(
    title="Pecha API",
    description="This is the API documentation for Pecha application",
    root_path="/api/v1",
    openapi_url="/docs/openapi.json",
    redoc_url="/docs"
)
api.include_router(auth_views.auth_router)


@api.get("/health", status_code=status.HTTP_204_NO_CONTENT)
async def get_health():
    return {'status': 'up'}

if __name__ == "__main__":
    uvicorn.run("pecha_api.app:api", host="127.0.0.1", port=8000, reload=True)

