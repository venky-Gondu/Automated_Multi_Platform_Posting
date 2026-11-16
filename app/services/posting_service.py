
import asyncio
from datetime import datetime, timezone

from app.platforms.base import BasePlatform
from app.schemas.response import PlatformResult, PostingResponse


class PostingService:

    def __init__(self, platforms: list[BasePlatform]):
        self.platforms = platforms

    async def publish(self, message: str) -> PostingResponse:

        tasks = [
            platform.publish(message)
            for platform in self.platforms
        ]

        outcomes = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        results: list[PlatformResult] = []

        for platform, outcome in zip(self.platforms, outcomes):

            if isinstance(outcome, BaseException):
                result = PlatformResult(
                    platform=platform.name,
                    status="failed",
                    error="Unexpected platform integration error."
                )
            else:
                result = outcome

            if result.status == "success" and result.posted_at is None:
                result.posted_at = datetime.now(timezone.utc)

            results.append(result)

        return PostingResponse(
            success=any(
                result.status == "success"
                for result in results
            ),
            results=results,
            completed_at=datetime.now(timezone.utc)
        )
