import uuid
import pytest
from unittest.mock import patch, AsyncMock

import pecha_api.plans.authors.plan_authors_views as views
from pecha_api.plans.authors.plan_authors_response_models import (
    AuthorInfoResponse,
    AuthorsResponse,
    AuthorInfoRequest,
    AuthorUpdateResponse,
    AuthorPlansResponse,
    AuthorPlanDTO,
)
from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO
from pecha_api.plans.plans_enums import PlanStatus


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


def _get_route_endpoint(path_suffix: str, method: str):
    for route in views.author_router.routes:
        if getattr(route, "path", "").endswith(path_suffix) and method in getattr(route, "methods", set()):
            return route.endpoint
    raise AssertionError(f"Route with suffix '{path_suffix}' and method '{method}' not found")


@pytest.mark.asyncio
async def test_get_all_authors_success():
    expected = AuthorsResponse(authors=[], skip=0, limit=20, total=0)

    with patch(
        "pecha_api.plans.authors.plan_authors_views.get_authors",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_service:
        resp = await views.get_all_authors()

        mock_service.assert_awaited_once()
        assert resp == expected


@pytest.mark.asyncio
async def test_get_author_information_self_success():
    creds = _Creds(token="tkn123")
    expected = AuthorInfoResponse(
        id=uuid.uuid4(),
        firstname="A",
        lastname="B",
        email="a@example.com",
        image_url=None,
        bio=None,
        social_profiles=[],
    )

    get_info_endpoint = _get_route_endpoint(path_suffix="/info", method="GET")

    with patch(
        "pecha_api.plans.authors.plan_authors_views.get_author_details",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_service:
        resp = await get_info_endpoint(authentication_credential=creds)

        mock_service.assert_awaited_once_with(token="tkn123")
        assert resp == expected


@pytest.mark.asyncio
async def test_update_author_information_success():
    creds = _Creds(token="token-xyz")
    request = AuthorInfoRequest(
        firstname="John",
        lastname="Doe",
        image_url=None,
        bio="bio",
        social_profiles=[],
    )
    expected = AuthorUpdateResponse(
        id=uuid.uuid4(),
        firstname="John",
        lastname="Doe",
        email="john@example.com",
        image_url="https://example.com/john.jpg",
        image_key="images/authors/john.jpg",
        bio="bio",
    )

    post_info_endpoint = _get_route_endpoint(path_suffix="/info", method="POST")

    with patch(
        "pecha_api.plans.authors.plan_authors_views.update_author_info",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_service:
        resp = await post_info_endpoint(authentication_credential=creds, author_info_request=request)

        mock_service.assert_awaited_once_with(token="token-xyz", author_info_request=request)
        assert resp == expected


@pytest.mark.asyncio
async def test_get_selected_author_information_success():
    author_id = uuid.uuid4()
    expected = AuthorInfoResponse(
        id=author_id,
        firstname="Jane",
        lastname="Doe",
        email="jane@example.com",
        image_url=None,
        bio=None,
        social_profiles=[],
    )

    # Due to duplicate function names in the module, resolve via router
    get_by_id_endpoint = _get_route_endpoint(path_suffix="/{author_id}", method="GET")

    with patch(
        "pecha_api.plans.authors.plan_authors_views.get_selected_author_details",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_service:
        resp = await get_by_id_endpoint(author_id=author_id)

        mock_service.assert_awaited_once_with(author_id=author_id)
        assert resp == expected


@pytest.mark.asyncio
async def test_get_plans_for_selected_author_success():
    author_id = uuid.uuid4()
    expected = AuthorPlansResponse(
        plans=[
            AuthorPlanDTO(
                id=uuid.uuid4(),
                title="P",
                description="D",
                language="en",
                image_url=None,
            )
        ],
        skip=0,
        limit=10,
        total=1,
    )

    get_plans_endpoint = _get_route_endpoint(path_suffix="/{author_id}/plans", method="GET")

    with patch(
        "pecha_api.plans.authors.plan_authors_views.get_plans_by_author",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_service:
        resp = await get_plans_endpoint(author_id=author_id)

        # View forwards author_id with pagination defaults skip=0, limit=10
        mock_service.assert_awaited_once_with(author_id=author_id, skip=0, limit=10)
        assert resp == expected


