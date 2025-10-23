import uuid
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException
from starlette import status

from pecha_api.app import api
from pecha_api.plans.items.plan_items_response_models import ItemDTO


VALID_TOKEN = "valid_token"


@pytest.fixture
def authenticated_client():
    from pecha_api.plans.items import plan_items_views

    original_dependency_overrides = api.dependency_overrides.copy()

    def get_token_override():
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=VALID_TOKEN)

    api.dependency_overrides[plan_items_views.oauth2_scheme] = get_token_override
    client = TestClient(api)

    yield client

    api.dependency_overrides = original_dependency_overrides


@pytest.fixture
def unauthenticated_client():
    original_dependency_overrides = api.dependency_overrides.copy()
    client = TestClient(api)
    yield client
    api.dependency_overrides = original_dependency_overrides


def test_create_day_success(authenticated_client):
    plan_id = uuid.uuid4()
    created = ItemDTO(id=uuid.uuid4(), plan_id=plan_id, day_number=4)

    with patch("pecha_api.plans.items.plan_items_views.create_plan_item", return_value=created) as mock_create:
        response = authenticated_client.post(f"/cms/plans/{plan_id}/days", headers={"Authorization": f"Bearer {VALID_TOKEN}"})

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["id"] == str(created.id)
        assert body["plan_id"] == str(plan_id)
        assert body["day_number"] == 4
        mock_create.assert_called_once()


def test_create_day_unauthorized(unauthenticated_client):
    plan_id = uuid.uuid4()
    response = unauthenticated_client.post(f"/cms/plans/{plan_id}/days")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_day_service_error(authenticated_client):
    plan_id = uuid.uuid4()
    with patch("pecha_api.plans.items.plan_items_views.create_plan_item") as mock_create:
        mock_create.side_effect = HTTPException(status_code=404, detail={"error": "Bad request", "message": "plan not found"})

        response = authenticated_client.post(f"/cms/plans/{plan_id}/days", headers={"Authorization": f"Bearer {VALID_TOKEN}"})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == {"error": "Bad request", "message": "plan not found"}


def test_delete_day_success(authenticated_client):
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()

    with patch("pecha_api.plans.items.plan_items_views.delete_plan_day_by_id", return_value=None) as mock_delete:
        response = authenticated_client.delete(
            f"/cms/plans/{plan_id}/days/{day_id}", headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # No content returned for 204
        assert response.text == ""
        mock_delete.assert_called_once()


def test_delete_day_unauthorized(unauthenticated_client):
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()
    response = unauthenticated_client.delete(f"/cms/plans/{plan_id}/days/{day_id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_day_not_found(authenticated_client):
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()

    with patch("pecha_api.plans.items.plan_items_views.delete_plan_day_by_id") as mock_delete:
        mock_delete.side_effect = HTTPException(status_code=404, detail={"error": "Not Found", "message": "day not found"})

        response = authenticated_client.delete(
            f"/cms/plans/{plan_id}/days/{day_id}", headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == {"error": "Not Found", "message": "day not found"}
