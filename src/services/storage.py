import json
from uuid import uuid4

import boto3
from fastapi import UploadFile

from src.core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )


def ensure_bucket_exists() -> None:
    s3 = get_s3_client()

    existing_buckets = s3.list_buckets()["Buckets"]
    bucket_names = [bucket["Name"] for bucket in existing_buckets]

    if settings.S3_BUCKET_NAME not in bucket_names:
        s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{settings.S3_BUCKET_NAME}/*"],
            }
        ],
    }

    s3.put_bucket_policy(
        Bucket=settings.S3_BUCKET_NAME,
        Policy=json.dumps(policy),
    )


async def upload_avatar(file: UploadFile, user_id: int) -> str:
    ensure_bucket_exists()

    filename = file.filename or "avatar.jpg"
    file_extension = filename.rsplit(".", 1)[-1]
    object_key = f"avatars/user_{user_id}/{uuid4()}.{file_extension}"

    s3 = get_s3_client()

    s3.upload_fileobj(
        file.file,
        settings.S3_BUCKET_NAME,
        object_key,
        ExtraArgs={
            "ContentType": file.content_type,
        },
    )

    return f"{settings.S3_PUBLIC_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{object_key}"
