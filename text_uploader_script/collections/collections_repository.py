from typing import Any
import asyncio

import requests

from text_uploader_script.constants import APPLICATION, DestinationURL, ACCESS_TOKEN
from text_uploader_script.collections.collection_model import CollectionPayload


async def get_collections(
    data_url: str, languages: list[str], parent_id: str | None = None
) -> list[dict[str, Any]]:
    """
    Fetch the list of collections (categories) from the remote API for
    a list of languages.

    The remote API expects `application` and `language` as query parameters,
    e.g. `...?application=webuddhist&language=en`.

    Returns a list in the form:

    [
        {
            "language": "en",
            "collections": [ ... raw API items ... ],
        },
        {
            "language": "bo",
            "collections": [ ... raw API items ... ],
        },
    ]
    """
    all_collections: list[dict[str, Any]] = []
    categories_url = f"{data_url}/v2/categories/"

    for language in languages:
        params = {
            "application": APPLICATION,
            "language": language,
            "parent_id": parent_id,
        }

        # `requests` is synchronous; run it in a thread so we can still await it.
        response = await asyncio.to_thread(
            requests.get,
            categories_url,
            params=params,
        )
        response.raise_for_status()

        all_collections.append(
            {
                "language": language,
                "collections": response.json(),
            }
        )

    return all_collections


async def post_collections(language: str, collections: CollectionPayload) -> dict[str, Any]:
    url = f"{DestinationURL.LOCAL.value}/collections"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    params = {"language": language}
    payload = collections.model_dump()

    # `requests` is synchronous; run it in a thread so we can still await it.
    response = await asyncio.to_thread(
        requests.post,
        url,
        headers=headers,
        params=params,
        json=payload,
    )

    if not response.ok:
        print(
            f"POST /collections failed "
            f"(language={language}) status={response.status_code} "
            f"body={response.text}"
        )
        response.raise_for_status()

    return response.json()


async def get_collection_by_pecha_collection_id(
    pecha_collection_id: str,
) -> dict[str, Any]:
    
    url = f"{DestinationURL.LOCAL.value}/collections/{pecha_collection_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    # `requests` is synchronous; run it in a thread so callers can still await.
    response = await asyncio.to_thread(
        requests.get,
        url,
        headers=headers
    )
    response.raise_for_status()

    return response.json()
