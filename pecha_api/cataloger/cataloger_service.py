import httpx
from pecha_api.cataloger.cataloger_response_model import CatalogedTextsDetailsResponse, ExternalPechaTextResponse
from pecha_api.error_contants import ErrorConstants
from pecha_api.http_message_utils import handle_http_status_error, handle_request_error
from ..config import get
from rich import print
from fastapi import HTTPException


client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))

async def get_cataloged_texts_details(text_id: str) -> CatalogedTextsDetailsResponse:
    if text_id is None:
        return None
    externalpecha_text=await call_external_pecha_api(text_id)
    print(externalpecha_text)
    #we will call external api and add status field here
    return None

async def call_external_pecha_api(
    text_id: str
):
    external_api_url = get("EXTERNAL_PECHA_API_URL")
    endpoint = f"{external_api_url}/texts/{text_id}"    
    try:
        response = await client.get(
            endpoint,
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        return ExternalPechaTextResponse(**data)
            
    except httpx.HTTPStatusError as e:
        handle_http_status_error(e)
    except httpx.RequestError as e:
        handle_request_error(e)