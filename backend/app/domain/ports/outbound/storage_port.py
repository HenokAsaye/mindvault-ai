from abc import ABC, abstractmethod
from typing import BinaryIO

class StoragePort(ABC):
    @abstractmethod
    async def upload_file(self, *, file: BinaryIO, file_key: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def download_file(self, *, file_key: str) -> BinaryIO:
        raise NotImplementedError

    @abstractmethod
    async def delete_file(self, *, file_key: str) -> None:
        raise NotImplementedError
