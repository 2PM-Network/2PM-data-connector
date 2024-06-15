from .submission import data_to_segments
from .provider import NHProvider


# TODO: convert it to a storage client
class ZeroGStorageClient:
    def __init__(self, url):
        self.provider = NHProvider(url)

    async def upload_file(self, data: bytes):
        segments = data_to_segments(data)
        segments = segments[:1]
        for segment in segments:
            await self.provider.upload_segment(segment)
        return True
