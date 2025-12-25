from typing import Optional
from starlette import status
from beanie import PydanticObjectId
from pecha_api.cataloger.cataloger_response_model import (
    CatalogedTextsDetailsResponse,
    CatalogedTextsResponse,
    CatalogedTexts,
    Title,
)
from pecha_api.error_contants import ErrorConstants
from ..config import get
from fastapi import HTTPException
from pecha_api.http_message_utils import handle_http_status_error, handle_request_error
import httpx
from pecha_api.constants import Constants


async def get_cataloged_texts_details(
    text_id: str, skip: int, limit: int
) -> Optional[CatalogedTextsDetailsResponse]:
    if text_id is None:
        return None
    # we will call external api and add status field here
    return None


async def get_cataloged_texts(
    search: Optional[str], skip: int, limit: int
) -> CatalogedTextsResponse:
    api_url = get("OPENPECHA_TEXTS_API_URL")

    try:
        params = {"type": Constants.TEXT_TYPE, "offset": skip, "limit": limit}
        if search:
            params["title"] = search
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            texts = [
                CatalogedTexts(
                    text_id=item["id"],
                    title=item.get("title", {}),
                    language=item["language"],
                    status=False,
                )
                for item in data
            ]

            return CatalogedTextsResponse(texts=texts)
    except httpx.HTTPStatusError as e:
        handle_http_status_error(e)
    except httpx.RequestError as e:
        handle_request_error(e)
