
import pytest
from typing import Literal

from app.services.posting_service import PostingService
from tests.conftest import FakePlatform


PlatformStatus = Literal["success", "failed", "skipped"]


@pytest.mark.asyncio
async def test_all_platforms_success():
    platforms = [
        FakePlatform("discord"),
        FakePlatform("telegram")
    ]

    response = await PostingService(platforms).publish(
        "Hello https://example.com"
    )

    assert response.success is True
    assert len(response.results) == 2
    assert all(r.status == "success" for r in response.results)


@pytest.mark.asyncio
async def test_partial_platform_failure():
    failed_status: PlatformStatus = "failed"

    platforms = [
        FakePlatform("discord"),
        FakePlatform("telegram", status=failed_status)
    ]

    response = await PostingService(platforms).publish(
        "Hello https://example.com"
    )

    assert response.success is True
    assert response.results[0].status == "success"
    assert response.results[1].status == "failed"


@pytest.mark.asyncio
async def test_unexpected_platform_exception():
    platforms = [
        FakePlatform("discord", should_raise=True),
        FakePlatform("telegram")
    ]

    response = await PostingService(platforms).publish(
        "Hello https://example.com"
    )

    assert response.success is True
    assert response.results[0].status == "failed"
    assert response.results[1].status == "success"
