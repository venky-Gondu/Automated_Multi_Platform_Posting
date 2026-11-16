
from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed", "skipped"]
    posted_url: str | None = None
    public_access: bool | None = None
    posted_at: datetime | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool
    results: list[PlatformResult]
    completed_at: datetime
