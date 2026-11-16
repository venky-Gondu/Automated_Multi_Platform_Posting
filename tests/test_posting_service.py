
import pytest
from typing import Literal

from app.platforms.base import BasePlatform
from app.schemas.response import PlatformResult
from app.services.posting_service import PostingService


PlatformStatus = Literal["success", "failed", "skipped"]


class FakePlatform(BasePlatform):

    def __init__(
        self,
        platform_name: str,
        status: PlatformStatus = "success",
        should_raise: bool = False
    ):
        self.platform_name = platform_name
        self.status = status
        self.should_raise = should_raise

    @property
    def name(self) -> str:
        return self.platform_name

    @property
    def is_configured(self) -> bool:
        return True

    async def publish(self, message: str) -> PlatformResult:

        if self.should_raise:
            raise RuntimeError("Simulated platform failure")

        return PlatformResult(
            platform=self.name,
            status=self.status
        )


@pytest.mark.asyncio
async def test_all_platforms_success():

    platforms = [
        FakePlatform("discord"),
        FakePlatform("telegram")
    ]

    service = PostingService(platforms)

    response = await service.publish("Hello https://example.com")

    assert response.success is True
    assert len(response.results) == 2
    assert all(r.status == "success" for r in response.results)


@pytest.mark.asyncio
async def test_partial_platform_failure():

    platforms = [
        FakePlatform("discord", "success"),
        FakePlatform("telegram", "failed")
    ]

    service = PostingService(platforms)

    response = await service.publish("Hello https://example.com")

    assert response.success is True
    assert response.results[0].status == "success"
    assert response.results[1].status == "failed"


@pytest.mark.asyncio
async def test_unexpected_platform_exception():

    platforms = [
        FakePlatform("discord", should_raise=True),
        FakePlatform("telegram")
    ]

    service = PostingService(platforms)

    response = await service.publish("Hello https://example.com")

    assert response.success is True
    assert response.results[0].status == "failed"
    assert response.results[1].status == "success"
