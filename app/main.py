
from fastapi import FastAPI

from app.core.config import settings
from app.platforms.discord import DiscordPlatform
from app.platforms.telegram import TelegramPlatform
from app.schemas.request import PostingRequest
from app.schemas.response import PostingResponse
from app.services.posting_service import PostingService


app = FastAPI(
    title="Automated Multi-Platform Posting API",
    description="Publish messages across multiple platforms through a single API.",
    version="1.0.0"
)

# Register available platform adapters
platforms = [
    DiscordPlatform(),
    TelegramPlatform()
]

# Inject adapters into the posting service
posting_service = PostingService(platforms=platforms)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "automated-posting"
    }


@app.post("/posting", response_model=PostingResponse)
async def create_post(request: PostingRequest):
    return await posting_service.publish(request.message)
