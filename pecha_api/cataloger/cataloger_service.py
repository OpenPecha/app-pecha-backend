import httpx
from pecha_api.cataloger.cataloger_response_model import CatalogedTextsDetailsResponse, ExternalPechaTextResponse, ExternalPechaInstanceRelatedResponse
from pecha_api.error_contants import ErrorConstants
from pecha_api.http_message_utils import handle_http_status_error, handle_request_error
from ..config import get
from rich import print
from fastapi import HTTPException
from pecha_api.constants import Constants


client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))

async def get_cataloged_texts_details(text_id: str) -> CatalogedTextsDetailsResponse | None:
    if text_id is None:
        return None
    externalpecha_text = await call_external_pecha_api_texts(text_id)
    print(externalpecha_text)
    externalpecha_instances = await call_external_pecha_api_instances(text_id)
    print(externalpecha_instances)
    for instance in externalpecha_instances:
        externalpecha_related_instances = await call_external_pecha_api_related_instances(instance)
        print(externalpecha_related_instances)
    
    raise HTTPException(status_code=501, detail="Cataloged text details endpoint not fully implemented")

async def call_external_pecha_api_texts(
    text_id: str
) -> ExternalPechaTextResponse:
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

async def call_external_pecha_api_instances(
    text_id: str
) -> list[str]:
    external_api_url = get("EXTERNAL_PECHA_API_URL")
    endpoint = f"{external_api_url}/texts/{text_id}/instances?instance_type={Constants.INSTANCE_TYPE}"   
    try:
        response = await client.get(
            endpoint,
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        return [item["id"] for item in data if "id" in item]
            
    except httpx.HTTPStatusError as e:
        handle_http_status_error(e)
    except httpx.RequestError as e:
        handle_request_error(e)

async def call_external_pecha_api_related_instances(
    id: str
) -> list[ExternalPechaInstanceRelatedResponse]:
    external_api_url = get("EXTERNAL_PECHA_API_URL")
    endpoint = f"{external_api_url}/instances/{id}/related"   
    try:
        response = await client.get(
            endpoint,
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        
        related_instances = []
        for item in data:
            metadata = item.get("metadata", {})
            related_instance = ExternalPechaInstanceRelatedResponse(
                title=metadata.get("title", {}),
                text_id=metadata.get("text_id", ""),
                language=metadata.get("language", ""),
                relation_type=item.get("relationship", "")
            )
            related_instances.append(related_instance)
        
        return related_instances
                    
    except httpx.HTTPStatusError as e:
        handle_http_status_error(e)
    except httpx.RequestError as e:
        handle_request_error(e)