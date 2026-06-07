import boto3
import asyncio
from typing import BinaryIO

from app.domain.ports.outbound.storage_port import StoragePort

class S3Storage(StoragePort):
    def __init__(self, *, bucket_name: str, access_key: str, secret_key: str) -> None:
        self._bucket_name = bucket_name
        self._s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        async def upload_file(
            self, *, file: BinaryIO, file_key: str, content_type: str
        ) -> str:
            await asyncio.to_thread(
                self._s3_client.upload_fileobj,
                Fileobj=file,
                Bucket=self._bucket_name,
                Key=file_key,
                ExtraArgs={"content_type": content_type},
            )
            return file_key
