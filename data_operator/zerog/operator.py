from .submission import data_to_segments
from .provider import NHProvider
import asyncio


# TODO: convert it to a storage client
class ZeroGStorageClient:
    def __init__(self, url):
        self.provider = NHProvider(url)

    async def upload_file(self, data: bytes):
        segments = data_to_segments(data)
        for segment in segments:
            await self.provider.upload_segment(segment)
        return True

    async def register_file(self, task: asyncio.Task):
        file_path = await task
        with open(file_path, "rb") as f:
            data = f.read()
        await self.upload_file(data)
