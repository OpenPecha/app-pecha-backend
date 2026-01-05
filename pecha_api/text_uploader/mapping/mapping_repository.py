from pecha_api.text_uploader.constants import SQSURL
from pecha_api.config import get_int

import httpx

async def trigger_mapping_repo(text_ids: list[str]):

    url = f"{SQSURL.DEVELOPMENT.value}/job/text-ids"
    headers = {
        "Content-Type": "application/json",
    }
    timeout = get_int("SQS_TIMEOUT")
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            url,
            json=text_ids,
            headers=headers
        )
        response.raise_for_status()
        return response.json()