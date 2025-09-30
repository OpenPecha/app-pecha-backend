from pecha_api.utils import Utils
from unittest.mock import patch, AsyncMock, Mock, MagicMock
import pytest
from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache
)
from pecha_api.users.user_response_models import (
    UserInfoResponse
)

from pecha_api.users.user_cache_service import (
    get_user_info_cache,
    set_user_info_cache,
    update_user_info_cache
)

from pecha_api.cache.cache_enums import CacheType

@pytest.mark.asyncio
async def test_get_user_info_cache_empty_cache():
    with patch("pecha_api.users.user_cache_service.get_cache_data", new_callable=AsyncMock, return_value=None):
    
        response = await get_user_info_cache(token="token", cache_type=CacheType.USER_INFO)

        assert response is None

@pytest.mark.asyncio
async def test_get_user_info_cache_success():
    mock_cache_data = UserInfoResponse(
        username="username_1",
        email="email_1",
        firstname="firstname_1",
        lastname="lastname_1",
        avatar_url="avatar_url_1",
        educations=["education_1"],
        followers=1,
        following=1,
        social_profiles=[]
    )
    with patch("pecha_api.users.user_cache_service.get_cache_data", new_callable=AsyncMock, return_value=mock_cache_data):

        response = await get_user_info_cache(token="token", cache_type=CacheType.USER_INFO)

        assert response is not None
        assert isinstance(response, UserInfoResponse)
        assert response.email == mock_cache_data.email

@pytest.mark.asyncio
async def test_set_user_info_cache_success():
    mock_cache_data = UserInfoResponse(
        username="username_1",
        email="email_1",
        firstname="firstname_1",
        lastname="lastname_1",
        avatar_url="avatar_url_1",
        educations=["education_1"],
        followers=1,
        following=1,
        social_profiles=[]
    )
    with patch("pecha_api.users.user_cache_service.set_cache", new_callable=AsyncMock):
        
        await set_user_info_cache(token="token", data=mock_cache_data, cache_type=CacheType.USER_INFO)


@pytest.mark.asyncio
async def test_update_user_info_cache_updates_existing():
    mock_cache_data = UserInfoResponse(
        username="username_1",
        email="email_1",
        firstname="firstname_1",
        lastname="lastname_1",
        avatar_url="avatar_url_1",
        educations=["education_1"],
        followers=1,
        following=1,
        social_profiles=[]
    )

    with patch("pecha_api.users.user_cache_service.update_cache", new_callable=AsyncMock, return_value=True) as mock_update, \
         patch("pecha_api.users.user_cache_service.set_cache", new_callable=AsyncMock) as mock_set:

        result = await update_user_info_cache(token="token", data=mock_cache_data, cache_type=CacheType.USER_INFO)

        assert result is True
        assert mock_update.await_count == 1
        assert mock_set.await_count == 0


@pytest.mark.asyncio
async def test_update_user_info_cache_sets_when_missing():
    mock_cache_data = UserInfoResponse(
        username="username_1",
        email="email_1",
        firstname="firstname_1",
        lastname="lastname_1",
        avatar_url="avatar_url_1",
        educations=["education_1"],
        followers=1,
        following=1,
        social_profiles=[]
    )

    with patch("pecha_api.users.user_cache_service.update_cache", new_callable=AsyncMock, return_value=False) as mock_update, \
         patch("pecha_api.users.user_cache_service.set_cache", new_callable=AsyncMock, return_value=True) as mock_set:

        result = await update_user_info_cache(token="token", data=mock_cache_data, cache_type=CacheType.USER_INFO)

        assert result is True
        assert mock_update.await_count == 1
        assert mock_set.await_count == 1
