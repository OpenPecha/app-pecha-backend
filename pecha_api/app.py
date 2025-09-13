from fastapi import FastAPI
from starlette import status
from fastapi.middleware.cors import CORSMiddleware

from pecha_api.auth.auth_service import retrieve_client_info

from pecha_api.db.mongo_database import lifespan
from pecha_api.auth import auth_views
from pecha_api.sheets import sheets_views
from pecha_api.collections import collections_views
from pecha_api.terms import terms_views
from pecha_api.texts import texts_views
from pecha_api.topics import topics_views
from pecha_api.users import users_views
from pecha_api.texts.mappings import mappings_views
from pecha_api.texts.segments import segments_views
from pecha_api.texts.groups import groups_views
from pecha_api.share import share_views
from pecha_api.search import search_views
from pecha_api.plans.auth import plan_auth_views
from pecha_api.plans.cms import views as cms_plans_views
from pecha_api.plans.public import views as public_plans_views
from pecha_api.plans.user import views as user_plans_views
from pecha_api.plans.image_upload import media_views
import uvicorn


api = FastAPI(
    title="Pecha API",
    description="This is the API documentation for Pecha application",
    root_path="/api/v1",
    redoc_url="/docs",
    lifespan=lifespan
)
api.include_router(auth_views.auth_router)
api.include_router(sheets_views.sheets_router)
api.include_router(collections_views.collections_router)
api.include_router(terms_views.terms_router)
api.include_router(texts_views.text_router)
api.include_router(groups_views.group_router)
api.include_router(segments_views.segment_router)
api.include_router(topics_views.topics_router)
api.include_router(users_views.user_router)
api.include_router(mappings_views.mapping_router)
api.include_router(search_views.search_router)
api.include_router(share_views.share_router)
api.include_router(plan_auth_views.plan_auth_router)
api.include_router(media_views.media_router)
api.include_router(cms_plans_views.cms_plans_router)
api.include_router(public_plans_views.public_plans_router)
api.include_router(user_plans_views.user_progress_router)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/props", status_code=status.HTTP_200_OK)
async def get_props():
   return retrieve_client_info()


@api.get("/health", status_code=status.HTTP_204_NO_CONTENT)
async def get_health():
    return {'status': 'up'}

if __name__ == "__main__":
    uvicorn.run("pecha_api.app:api", host="127.0.0.1", port=8000, reload=True)
