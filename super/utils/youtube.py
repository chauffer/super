from functools import partial

import aioyoutube

from super import SUPER_YOUTUBE_API_KEY


class YT:
    def __init__(self):
        self.api = aioyoutube.Api()

    async def search_videos(self, text, limit=5):
        results = await self.api.search(
            key=SUPER_YOUTUBE_API_KEY, text=text, max_results=5
        )

        metadata = await self.api.videos(
            key=SUPER_YOUTUBE_API_KEY,
            video_ids=[video["id"]["videoId"] for video in results["items"]],
            part=["snippet", "contentDetails"],
        )

        return metadata

    async def metadata(self, video_id):
        print("md", video_id)
        return (
            await self.api.videos(
                key=SUPER_YOUTUBE_API_KEY,
                video_ids=[video_id],
                part=["snippet", "contentDetails"],
            )
        )["items"][0]
