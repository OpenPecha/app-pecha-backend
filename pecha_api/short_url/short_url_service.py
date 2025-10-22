from pecha_api.config import get
from pecha_api.share.share_response_models import ShortUrlResponse
from http import HTTPStatus
import httpx
from starlette.responses import Response

async def get_short_url(payload: dict) -> ShortUrlResponse:

    short_url_endpoint = get("SHORT_URL_GENERATION_ENDPOINT")
    url = f"{short_url_endpoint}/"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code == HTTPStatus.CREATED:
            data = response.json()
            short_url = data["short_url"]
            return ShortUrlResponse(
                shortUrl=short_url
            )
        else:
            # Pass through the exact response from the server
            return Response(
                content=response.content, 
                status_code=response.status_code, 
                media_type=response.headers.get('content-type', 'application/json')
            )