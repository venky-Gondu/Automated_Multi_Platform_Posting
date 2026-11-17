
import pytest

from app.services.posting_service import PostingService
from tests.conftest import FakePlatform, FakeURLChecker


@pytest.mark.asyncio
async def test_all_platforms_success():
    platforms = [
        FakePlatform("discord"),
        FakePlatform("telegram")
    ]

    service = PostingService(platforms, FakeURLChecker())
    response = await service.publish("Hello https://example.com")

    assert response.success is True
    assert len(response.results) == 2
    assert all(result.status == "success" for result in response.results)
    assert response.url_check.status == "reachable"


@pytest.mark.asyncio
async def test_partial_platform_failure():
    platforms = [
        FakePlatform("discord"),
        FakePlatform("telegram", status="failed")
    ]

    service = PostingService(platforms, FakeURLChecker())
    response = await service.publish("Hello https://example.com")

    assert response.success is True
    assert response.results[0].status == "success"
    assert response.results[1].status == "failed"
    assert response.url_check.status == "reachable"


@pytest.mark.asyncio
async def test_unexpected_platform_exception():
    platforms = [
        FakePlatform("discord", should_raise=True),
        FakePlatform("telegram")
    ]

    service = PostingService(platforms, FakeURLChecker())
    response = await service.publish("Hello https://example.com")

    assert response.success is True
    assert response.results[0].status == "failed"
    assert response.results[1].status == "success"
    assert response.url_check.status == "reachable"


@pytest.mark.asyncio
async def test_unreachable_url_does_not_block_publishing():
    platforms = [
        FakePlatform("discord"),
        FakePlatform("telegram")
    ]

    service = PostingService(
        platforms,
        FakeURLChecker(status="unreachable")
    )

    response = await service.publish(
        "Check our website https://example.com"
    )

    assert response.url_check.status == "unreachable"
    assert response.url_check.warning is not None

    assert response.success is True
    assert all(
        result.status == "success"
        for result in response.results
    )
