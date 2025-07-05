from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from uuid import uuid4

from pecha_api.texts.texts_repository import fetch_sheets_from_db
from pecha_api.texts.texts_models import Text
from pecha_api.texts.texts_enums import TextType
from pecha_api.sheets.sheets_enum import SortBy, SortOrder


@pytest.mark.asyncio
async def test_fetch_sheets_from_db_default_parameters():
    """Test fetch_sheets_from_db with default parameters"""
    # Mock Text objects
    mock_text_1 = MagicMock()
    mock_text_1.id = str(uuid4())
    mock_text_1.title = "Test Sheet 1"
    mock_text_1.language = "bo"
    mock_text_1.group_id = "group_1"
    mock_text_1.type = TextType.SHEET
    mock_text_1.is_published = True
    mock_text_1.created_date = "2024-01-01 10:00:00"
    mock_text_1.updated_date = "2024-01-01 10:00:00"
    mock_text_1.published_date = "2024-01-01 10:00:00"
    mock_text_1.published_by = "test@example.com"
    mock_text_1.categories = []
    mock_text_1.views = 100

    mock_text_2 = MagicMock()
    mock_text_2.id = str(uuid4())
    mock_text_2.title = "Test Sheet 2"
    mock_text_2.language = "en"
    mock_text_2.group_id = "group_2"
    mock_text_2.type = TextType.SHEET
    mock_text_2.is_published = True
    mock_text_2.created_date = "2024-01-02 15:30:00"
    mock_text_2.updated_date = "2024-01-02 15:30:00"
    mock_text_2.published_date = "2024-01-02 15:30:00"
    mock_text_2.published_by = "another@example.com"
    mock_text_2.categories = []
    mock_text_2.views = 250

    mock_sheets = [mock_text_1, mock_text_2]

    with patch.object(Text, 'get_sheets', new_callable=AsyncMock, return_value=mock_sheets) as mock_get_sheets:
        result = await fetch_sheets_from_db()

        # Verify the result
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert result == mock_sheets

        # Verify Text.get_sheets was called with correct default parameters
        mock_get_sheets.assert_called_once_with(
            published_by=None,
            is_published=None,
            sort_by=None,
            sort_order=None,
            skip=0,
            limit=10
        )


@pytest.mark.asyncio
async def test_fetch_sheets_from_db_with_all_parameters():
    """Test fetch_sheets_from_db with all parameters specified"""
    mock_sheets = []

    with patch.object(Text, 'get_sheets', new_callable=AsyncMock, return_value=mock_sheets) as mock_get_sheets:
        result = await fetch_sheets_from_db(
            published_by="test@example.com",
            is_published=True,
            sort_by=SortBy.PUBLISHED_DATE,
            sort_order=SortOrder.DESC,
            skip=20,
            limit=5
        )

        # Verify the result
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0
        assert result == mock_sheets

        # Verify Text.get_sheets was called with correct parameters
        mock_get_sheets.assert_called_once_with(
            published_by="test@example.com",
            is_published=True,
            sort_by=SortBy.PUBLISHED_DATE,
            sort_order=SortOrder.DESC,
            skip=20,
            limit=5
        )


@pytest.mark.asyncio
async def test_fetch_sheets_from_db_with_partial_parameters():
    """Test fetch_sheets_from_db with partial parameters"""
    mock_text = MagicMock()
    mock_text.id = str(uuid4())
    mock_text.title = "Filtered Sheet"
    mock_text.language = "bo"
    mock_text.group_id = "group_1"
    mock_text.type = TextType.SHEET
    mock_text.is_published = False
    mock_text.created_date = "2024-01-01 10:00:00"
    mock_text.updated_date = "2024-01-01 10:00:00"
    mock_text.published_date = "2024-01-01 10:00:00"
    mock_text.published_by = "specific@example.com"
    mock_text.categories = []
    mock_text.views = 50

    mock_sheets = [mock_text]

    with patch.object(Text, 'get_sheets', new_callable=AsyncMock, return_value=mock_sheets) as mock_get_sheets:
        result = await fetch_sheets_from_db(
            published_by="specific@example.com",
            is_published=False,
            skip=5
        )

        # Verify the result
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == mock_text

        # Verify Text.get_sheets was called with correct parameters
        mock_get_sheets.assert_called_once_with(
            published_by="specific@example.com",
            is_published=False,
            sort_by=None,
            sort_order=None,
            skip=5,
            limit=10
        )


@pytest.mark.asyncio
async def test_fetch_sheets_from_db_empty_result():
    """Test fetch_sheets_from_db when no sheets are found"""
    with patch.object(Text, 'get_sheets', new_callable=AsyncMock, return_value=[]) as mock_get_sheets:
        result = await fetch_sheets_from_db()

        # Verify the result
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

        # Verify Text.get_sheets was called
        mock_get_sheets.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_sheets_from_db_with_sort_by_created_date():
    """Test fetch_sheets_from_db with sort by created date"""
    mock_sheets = []

    with patch.object(Text, 'get_sheets', new_callable=AsyncMock, return_value=mock_sheets) as mock_get_sheets:
        result = await fetch_sheets_from_db(
            sort_by=SortBy.CREATED_DATE,
            sort_order=SortOrder.ASC
        )

        # Verify the result
        assert result is not None
        assert isinstance(result, list)

        # Verify Text.get_sheets was called with correct sorting parameters
        mock_get_sheets.assert_called_once_with(
            published_by=None,
            is_published=None,
            sort_by=SortBy.CREATED_DATE,
            sort_order=SortOrder.ASC,
            skip=0,
            limit=10
        )


@pytest.mark.asyncio
async def test_fetch_sheets_from_db_large_skip_and_limit():
    """Test fetch_sheets_from_db with large skip and limit values"""
    mock_sheets = []

    with patch.object(Text, 'get_sheets', new_callable=AsyncMock, return_value=mock_sheets) as mock_get_sheets:
        result = await fetch_sheets_from_db(skip=100, limit=50)

        # Verify the result
        assert result is not None
        assert isinstance(result, list)

        # Verify Text.get_sheets was called with correct pagination parameters
        mock_get_sheets.assert_called_once_with(
            published_by=None,
            is_published=None,
            sort_by=None,
            sort_order=None,
            skip=100,
            limit=50
        )


@pytest.mark.asyncio
async def test_fetch_sheets_from_db_published_only():
    """Test fetch_sheets_from_db filtering for published sheets only"""
    mock_text = MagicMock()
    mock_text.id = str(uuid4())
    mock_text.title = "Published Sheet"
    mock_text.is_published = True
    mock_text.type = TextType.SHEET

    mock_sheets = [mock_text]

    with patch.object(Text, 'get_sheets', new_callable=AsyncMock, return_value=mock_sheets) as mock_get_sheets:
        result = await fetch_sheets_from_db(is_published=True)

        # Verify the result
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1

        # Verify Text.get_sheets was called with is_published=True
        mock_get_sheets.assert_called_once_with(
            published_by=None,
            is_published=True,
            sort_by=None,
            sort_order=None,
            skip=0,
            limit=10
        )


@pytest.mark.asyncio
async def test_fetch_sheets_from_db_unpublished_only():
    """Test fetch_sheets_from_db filtering for unpublished sheets only"""
    mock_text = MagicMock()
    mock_text.id = str(uuid4())
    mock_text.title = "Draft Sheet"
    mock_text.is_published = False
    mock_text.type = TextType.SHEET

    mock_sheets = [mock_text]

    with patch.object(Text, 'get_sheets', new_callable=AsyncMock, return_value=mock_sheets) as mock_get_sheets:
        result = await fetch_sheets_from_db(is_published=False)

        # Verify the result
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1

        # Verify Text.get_sheets was called with is_published=False
        mock_get_sheets.assert_called_once_with(
            published_by=None,
            is_published=False,
            sort_by=None,
            sort_order=None,
            skip=0,
            limit=10
        ) 