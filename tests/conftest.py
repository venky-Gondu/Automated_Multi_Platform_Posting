
from datetime import datetime, timezone
from typing import Literal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.platforms.base import BasePlatform
from app.schemas.response import PlatformResult, PostingResponse


PlatformStatus = Literal["success", "failed", "skipped"]


# Shared fake platform for service tests
class FakePlatform(BasePlatform):

    def __init__(
        self,
        platform_name: str,
        status: PlatformStatus = "success",
        should_raise: bool = False
    ):
        self.platform_name = platform_name
        self.status: PlatformStatus = status
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


# Shared fake service for API tests
class FakePostingService:

    async def publish(self, message: str) -> PostingResponse:
        return PostingResponse(
            success=True,
            results=[
                PlatformResult(platform="discord", status="success"),
                PlatformResult(platform="telegram", status="success")
            ],
            completed_at=datetime.now(timezone.utc)
        )


# Shared API client
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


# Shared fake posting service
@pytest.fixture
def fake_posting_service():
    return FakePostingService()
