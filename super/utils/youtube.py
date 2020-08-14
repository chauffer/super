from functools import partial

import aniso8601
import aioyoutube
import structlog

from super.settings import SUPER_YOUTUBE_API_KEY
from super.settings import SUPER_MAX_YOUTUBE_LENGTH


logger = structlog.getLogger(__name__)


class YT:
    def __init__(self):
        self.api = aioyoutube.Api()

    async def search_videos(self, text, limit=5):
        logger.debug("utils/youtube/search_videos: Searching", text=text, limit=limit)
        results = await self.api.search(
            key=SUPER_YOUTUBE_API_KEY, text=text, max_results=limit, order="relevance"
        )

        logger.debug("utils/youtube/search_videos: Fetching metadatas")
        metadata = await self.api.videos(
            key=SUPER_YOUTUBE_API_KEY,
            video_ids=[
                video["id"]["videoId"]
                for video in results["items"]
                if video["snippet"]["liveBroadcastContent"] == "none"
            ],
            part=["snippet", "contentDetails"],
        )

        return [
            video
            for video in metadata["items"]
            if aniso8601.parse_duration(video["contentDetails"]["duration"]).seconds
            < SUPER_MAX_YOUTUBE_LENGTH
        ][:5]

    async def metadata(self, video_id):
        logger.debug("utils/youtube/metadata: Fetching", video_id=video_id)
        return (
            await self.api.videos(
                key=SUPER_YOUTUBE_API_KEY,
                video_ids=[video_id],
                part=["snippet", "contentDetails"],
            )
        )["items"][0]
