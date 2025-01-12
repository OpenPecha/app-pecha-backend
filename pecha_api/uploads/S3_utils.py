import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
import logging

from starlette import status

from ..config import get

s3_client = boto3.client(
    "s3",
    aws_access_key_id=get("AWS_ACCESS_KEY"),
    aws_secret_access_key=get("AWS_SECRET_KEY"),
    region_name=get("AWS_REGION")

)


def upload_file(bucket_name: str, s3_key: str, file: UploadFile) -> str:

    try:
        s3_client.upload_fileobj(
            Fileobj=file.file,
            Bucket=bucket_name,
            Key=s3_key,
            ExtraArgs={"ContentType": file.content_type}
        )
        return s3_key
    except ClientError as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to upload file to S3.")
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An unexpected error occurred.")


def delete_file(file_path: str):
    try:
        s3_client.delete_object(Bucket=get("AWS_BUCKET_NAME"), Key=file_path)
        return True
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] != 'NoSuchKey':
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting old image.")

