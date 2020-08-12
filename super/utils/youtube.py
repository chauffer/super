from functools import partial

import aniso8601
import aioyoutube

from super.settings import SUPER_YOUTUBE_API_KEY
from super.settings import SUPER_MAX_YOUTUBE_LENGTH


class YT:
    def __init__(self):
        self.api = aioyoutube.Api()

    async def search_videos(self, text, limit=5):
        results = await self.api.search(
            key=SUPER_YOUTUBE_API_KEY, text=text, max_results=limit, order="relevance"
        )

        metadata = await self.api.videos(
            key=SUPER_YOUTUBE_API_KEY,
            video_ids=[
                video["id"]["videoId"]
                for video in results["items"]
                if video["snippet"]["liveBroadcastContent"] == "none"
                and aniso8601.parse_duration(
                    video["contentDetails"]["duration"]
                ).seconds
                < SUPER_MAX_YOUTUBE_LENGTH
            ],
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
