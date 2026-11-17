
from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class URLCheckResult(BaseModel):
    url: str
    status: Literal["reachable", "unreachable", "unknown"]
    warning: str | None = None


class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed", "skipped"]
    posted_id: str | None = None
    channel_id: str | None = None
    posted_url: str | None = None
    public_access: bool | None = None
    posted_at: datetime | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool
    url_check: URLCheckResult
    results: list[PlatformResult]
    completed_at: datetime
