
import asyncio
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Protocol

from app.platforms.base import BasePlatform
from app.schemas.request import extract_urls
from app.schemas.response import (
    PlatformResult,
    PostingResponse,
    URLCheckResult,
)


class URLCheckerProtocol(Protocol):
    async def check(self, url: str) -> URLCheckResult:
        ...


class PostingService:

    def __init__(
        self,
        platforms: Sequence[BasePlatform],
        url_checker: URLCheckerProtocol,
    ):
        self.platforms = platforms
        self.url_checker = url_checker

    async def publish(self, message: str) -> PostingResponse:

        urls = extract_urls(message)

        if len(urls) != 1:
            raise ValueError("Message must contain exactly one URL.")

        url = urls[0]

        outcomes = await asyncio.gather(
            self.url_checker.check(url),
            *(platform.publish(message) for platform in self.platforms),
            return_exceptions=True,
        )

        # Process URL checker result
        url_outcome = outcomes[0]

        if isinstance(url_outcome, asyncio.CancelledError):
            raise url_outcome

        if isinstance(url_outcome, URLCheckResult):
            url_result = url_outcome
        else:
            url_result = URLCheckResult(
                url=url,
                status="unknown",
                warning="URL availability check failed unexpectedly.",
            )

        # Process platform results
        results: list[PlatformResult] = []

        for platform, outcome in zip(self.platforms, outcomes[1:]):

            if isinstance(outcome, asyncio.CancelledError):
                raise outcome

            if isinstance(outcome, PlatformResult):
                result = outcome

            else:
                result = PlatformResult(
                    platform=platform.name,
                    status="failed",
                    error="Unexpected platform integration error.",
                )

            if result.status == "success" and result.posted_at is None:
                result.posted_at = datetime.now(timezone.utc)

            results.append(result)

        return PostingResponse(
            success=any(
                result.status == "success"
                for result in results
            ),
            url_check=url_result,
            results=results,
            completed_at=datetime.now(timezone.utc),
        )
