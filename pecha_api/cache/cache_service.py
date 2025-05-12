import hashlib

from pecha_api.texts.texts_response_models import (
    TextDetailsRequest
)

from pecha_api.texts.texts_response_models import DetailTableOfContentResponse

from .cache_repository import (
    set_cache, 
    get_cache_data
)

def set_text_details_cache(text_id: str = None, text_details_request: TextDetailsRequest = None, text_details: DetailTableOfContentResponse = None):
    params_str = f"{text_id}{text_details_request.content_id}{text_details_request.segment_id}{text_details_request.version_id}{text_details_request.section_id}{text_details_request.skip}{text_details_request.limit}"
    hash_value = hashlib.sha256(params_str.encode()).hexdigest()

    set_cache(hash_value, text_details)


def get_text_details_cache(text_id: str = None, text_details_request: TextDetailsRequest = None):

    params_str = f"{text_id}{text_details_request.content_id}{text_details_request.segment_id}{text_details_request.version_id}{text_details_request.section_id}{text_details_request.skip}{text_details_request.limit}"
    hash_value = hashlib.sha256(params_str.encode()).hexdigest()

    cache_data = get_cache_data(hash_value)

    return cache_data
