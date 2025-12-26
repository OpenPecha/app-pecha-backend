from typing import Any
import asyncio

import requests

# from text_uploader_script.config import APPLICATION, DestinationURL, ACCESS_TOKEN
from text_uploader_script.collections.collection_model import CollectionPayload


def _looks_like_slug_already_exists_error(response: requests.Response) -> tuple[bool, str | None]:
    """
    Detect the specific backend error we want to ignore:
      400 {"detail":"Collection with this slug <X> already exists"}
    """
    if response.status_code != 400:
        return False, None

    try:
        body = response.json()
    except Exception:
        return False, None

    if not isinstance(body, dict):
        return False, None

    detail = body.get("detail")
    if not isinstance(detail, str):
        return False, None

    normalized = detail.lower()
    if "collection" in normalized and "slug" in normalized and "already exists" in normalized:
        return True, detail

    return False, detail


def _first_collection_like(obj: Any) -> dict[str, Any] | None:
    """
    Normalise API responses that may return:
      - a single collection dict
      - a list of collection dicts
      - a wrapper dict like {"collections": [ ... ]}
    """
    if isinstance(obj, dict):
        if "collections" in obj and isinstance(obj.get("collections"), list):
            collections = obj.get("collections") or []
            if collections:
                first = collections[0]
                return first if isinstance(first, dict) else None
        return obj

    if isinstance(obj, list):
        if not obj:
            return None
        first = obj[0]
        return first if isinstance(first, dict) else None

    return None


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
        is_slug_exists, detail = _looks_like_slug_already_exists_error(response)
        if is_slug_exists:
            # Treat "slug already exists" as non-fatal and try to resolve the
            # existing destination record so downstream steps can still log the
            # mapping and attach children to the right parent.
            print(
                f"POST /collections skipped (already exists) "
                f"(language={language}) slug={collections.slug!r} "
                f"pecha_collection_id={collections.pecha_collection_id!r} detail={detail!r}"
            )

            # Try fetching by pecha_collection_id first (best-case for re-runs).
            existing: dict[str, Any] | None = None
            try:
                existing = await get_collection_by_pecha_collection_id(
                    collections.pecha_collection_id
                )
            except requests.HTTPError:
                existing = None

            # If that endpoint isn't supported, fall back to querying by slug.
            if not existing:
                try:
                    existing = await get_collection_by_slug(language, collections.slug)
                except requests.HTTPError:
                    existing = None

            if existing:
                return existing

            # If we can't resolve the existing record, still continue the run.
            return {
                "id": None,
                "already_exists": True,
                "detail": detail,
            }

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


async def get_collection_by_slug(language: str, slug: str) -> dict[str, Any]:
    """
    Best-effort lookup used when create fails due to unique slug constraint.

    The destination API may return:
      - a single object
      - a list of objects
      - a wrapper like {"collections": [...]}
    """
    url = f"{DestinationURL.LOCAL.value}/collections"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    params = {"language": language, "slug": slug}

    response = await asyncio.to_thread(
        requests.get,
        url,
        headers=headers,
        params=params,
    )
    response.raise_for_status()

    data = _first_collection_like(response.json())
    return data or {}
