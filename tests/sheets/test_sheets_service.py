from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from fastapi import HTTPException
from pecha_api.sheets.sheets_service import get_sheets_by_userID, create_new_sheet
from pecha_api.sheets.sheets_response_models import Publisher, CreateSheetRequest, SheetModel, SheetsResponse

@pytest.mark.asyncio
async def test_get_sheets_by_userID_en():
    with patch('pecha_api.sheets.sheets_service.get_user_by_username', new_callable=MagicMock, return_value=MagicMock(id="1", firstname="Tenzin", lastname="Tsering")), \
            patch('pecha_api.sheets.sheets_service.get_topic_by_id', new_callable=AsyncMock, return_value=AsyncMock(id="67cda8aca32f2d32016960fa", titles={"en": "From suffering to Happiness", "bo": "སྡུག་བསྔལ་བདེ་བར་བསྒྱུར་ཐབས།"})), \
            patch('pecha_api.sheets.sheets_service.get_users_sheets', new_callable=AsyncMock, return_value=[
                AsyncMock(id="1", titles="title 1", summaries="summary 1", published_date=1741531642524, views=0, likes=[], topic_id=["67cda8aca32f2d32016960fa"]),
                AsyncMock(id="2", titles="title 2", summaries="summary 2", published_date=1741531642524, views=0, likes=[], topic_id=["67cda8aca32f2d32016960fa"]),
            ]):
        response = await get_sheets_by_userID(user_id="tenzin_tsering.6630", language="en", skip=0, limit=10)
        assert response == SheetsResponse(sheets=[
            SheetModel(id="1", title="title 1", summary="summary 1", publisher=Publisher(id="1", name="Tenzin Tsering", profile_url="", image_url=""), published_date=1741531642524, time_passed=1741531642524, views=0, likes=[], topics=[{"en": "From suffering to Happiness", "bo": "སྡུག་བསྔལ་བདེ་བར་བསྒྱུར་ཐབས།"}], language="en"),
            SheetModel(id="2", title="title 2", summary="summary 2", publisher=Publisher(id="1", name="Tenzin Tsering", profile_url="", image_url=""), published_date=1741531642524, time_passed=1741531642524, views=0, likes=[], topics=[{"en": "From suffering to Happiness", "bo": "སྡུག་བསྔལ་བདེ་བར་བསྒྱུར་ཐབས།"}], language="en")
        ])

@pytest.mark.asyncio
async def test_get_sheets_by_userID_bo():
    with patch('pecha_api.sheets.sheets_service.get_user_by_username', new_callable=MagicMock, return_value=MagicMock(id="1", firstname="Tenzin", lastname="Tsering")), \
            patch('pecha_api.sheets.sheets_service.get_topic_by_id', new_callable=AsyncMock, return_value=AsyncMock(id="67cda8aca32f2d32016960fa", titles={"en": "From suffering to Happiness", "bo": "སྡུག་བསྔལ་བདེ་བར་བསྒྱུར་ཐབས།"})), \
            patch('pecha_api.sheets.sheets_service.get_users_sheets', new_callable=AsyncMock, return_value=[
                AsyncMock(id="1", titles="title 1", summaries="summary 1", published_date=1741531642524, views=0, likes=[], topic_id=["67cda8aca32f2d32016960fa"]),
                AsyncMock(id="2", titles="title 2", summaries="summary 2", published_date=1741531642524, views=0, likes=[], topic_id=["67cda8aca32f2d32016960fa"]),
            ]):
        response = await get_sheets_by_userID(user_id="tenzin_tsering.6630", language="bo", skip=0, limit=10)
        assert response == SheetsResponse(sheets=[
            SheetModel(id="1", title="title 1", summary="summary 1", publisher=Publisher(id="1", name="Tenzin Tsering", profile_url="", image_url=""), published_date=1741531642524, time_passed=1741531642524, views=0, likes=[], topics=[{"en": "From suffering to Happiness", "bo": "སྡུག་བསྔལ་བདེ་བར་བསྒྱུར་ཐབས།"}], language="bo"),
            SheetModel(id="2", title="title 2", summary="summary 2", publisher=Publisher(id="1", name="Tenzin Tsering", profile_url="", image_url=""), published_date=1741531642524, time_passed=1741531642524, views=0, likes=[], topics=[{"en": "From suffering to Happiness", "bo": "སྡུག་བསྔལ་བདེ་བར་བསྒྱུར་ཐབས།"}], language="bo")
        ])

# @pytest.mark.asyncio
# async def test_create_new_sheet():
#     with patch('pecha_api.sheets/sheets_service.create_new_sheet',
#                new_callable=AsyncMock) as mock_create_sheet, \
#             patch('pecha_api.config.get', return_value="en"):
#         mock_create_sheet.return_value = AsyncMock(id="1", titles="title 1", summaries="summary 1", source=[], topic_id=[], publisher_id="1", creation_date="utc date", modified_date="utc date", published_date=1234567890, views=0, likes=[], collection=[], sheetLanguage="en")
#         create_sheet_request = CreateSheetRequest(titles="title 1", summaries="summary 1", source=[], publisher_id="1", topic_id=[], sheetLanguage="en")
#         response = await create_new_sheet(create_sheet_request=create_sheet_request)
        