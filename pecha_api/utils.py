from typing import Optional
import io
import logging
from PIL import Image
from beanie import PydanticObjectId
from fastapi import HTTPException, UploadFile
from bson.errors import InvalidId
from starlette import status
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
from .config import get_int
from pecha_api.error_contants import ErrorConstants

from .constants import Constants


class Utils:

    @staticmethod
    def get_utc_date_time() -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_date_time_from_epoch(epoch: int) -> str:
        return datetime.fromtimestamp(epoch // 1000, timezone.utc)

    @staticmethod
    def time_passed(published_time: int, language: str) -> str:
        current_time = datetime.now(timezone.utc)
        post_time = datetime.fromtimestamp(published_time // 1000, timezone.utc)
        time_difference = current_time - post_time
        if time_difference < timedelta(minutes=1):
            return Utils.get_word_by_language(word='Now', language=language)
        elif time_difference < timedelta(hours=1):
            minutes = int(time_difference.total_seconds() / Constants.MINUTE_IN_SECONDS)
            minute_value = Utils.get_number_by_language(value=minutes, language=language)
            return f"{minute_value} {Utils.get_word_by_language(word='Min', language=language)}"
        elif time_difference < timedelta(days=1):
            hours = int(time_difference.total_seconds() / Constants.HOUR_IN_SECONDS)
            hour_value = Utils.get_number_by_language(value=hours, language=language)
            return f"{hour_value} {Utils.get_word_by_language(word='Hr', language=language)}"
        elif time_difference < timedelta(weeks=1):
            days = int(time_difference.total_seconds() / Constants.DAY_IN_SECONDS)
            days_value = Utils.get_number_by_language(value=days, language=language)
            return f"{days_value} {Utils.get_word_by_language(word='Day', language=language)}"
        else:
            return post_time.strftime('%Y-%m-%d %H:%M:%S')


    @staticmethod
    def get_value_from_dict(values: dict[str, str], language: str):
        value = "" if not isinstance(values, dict) or not values else values.get(language, "")
        return value

    @staticmethod
    def get_parent_id(parent_id: Optional[str]):
        topic_parent_id = None
        if parent_id is not None:
            try:
                topic_parent_id = PydanticObjectId(parent_id)
            except InvalidId as e:
                logging.debug(f"error with id: ${e}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Parent id")

        return topic_parent_id

    @staticmethod
    def get_number_by_language(value: int, language: str) -> str:
        return "".join(
            [Constants.LANGUAGE_NUMBER[language][char] if "0" <= char <= "9" else char for char in str(value)])

    @staticmethod
    def extract_s3_key(presigned_url: str) -> str:
        if not presigned_url:
            return ""
        parsed_url = urlparse(presigned_url)
        # Extract the path and remove the leading '/'
        s3_key = parsed_url.path.lstrip('/')
        if not s3_key:
            return ""
        return s3_key