from pecha_api.utils import Utils
from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache,
    delete_cache
)

from .sheets_response_models import (
    SheetDetailDTO,
    SheetDTOResponse
)

def get_fetch_sheets_cache(token: str = None, language: str = None, email: str = None, sort_by: str = None, sort_order: str = None, skip: int = 0, limit: int = 10) -> SheetDTOResponse:
    payload = [token, language, email, sort_by, sort_order, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SheetDTOResponse = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_fetch_sheets_cache(token: str = None, language: str = None, email: str = None, sort_by: str = None, sort_order: str = None, skip: int = 0, limit: int = 10, data: SheetDTOResponse = None):
    payload = [token, language, email, sort_by, sort_order, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_sheet_by_id_cache(sheet_id: str = None, skip: int = 0, limit: int = 10) -> SheetDetailDTO:
    payload = [sheet_id, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SheetDetailDTO = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_sheet_by_id_cache(sheet_id: str = None, skip: int = 0, limit: int = 10, data: SheetDetailDTO = None):
    payload = [sheet_id, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def delete_sheet_by_id_cache(sheet_id: str = None, skip: int = 0, limit: int = 10):
    payload = [sheet_id, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    delete_cache(hash_key = hashed_key)