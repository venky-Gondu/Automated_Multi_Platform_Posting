
import pytest

from app.core.config import settings
from app.platforms.discord import DiscordPlatform
from app.platforms.telegram import TelegramPlatform


class FakeResponse:

    def raise_for_status(self):
        pass

    def json(self):
        return {
            "id": "123456789012345678",
            "channel_id": "987654321098765432",
            "guild_id": "111111111111111111"
        }


class FakeAsyncClient:

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def post(self, *args, **kwargs):
        return FakeResponse()

class FakeTelegramResponse:

    def raise_for_status(self):
        pass

    def json(self):
        return {
            "ok": True,
            "result": {
                "message_id": 12345,
                "chat": {
                    "id": 123456789
                }
            }
        }


class FakeTelegramAsyncClient:

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass
    

    async def post(self, *args, **kwargs):
        return FakeTelegramResponse()

@pytest.mark.asyncio
async def test_discord_success(monkeypatch):

    monkeypatch.setattr(
        settings,
        "discord_webhook_url",
        "https://example.com/webhook"
    )

    monkeypatch.setattr(
        "app.platforms.discord.httpx.AsyncClient",
        FakeAsyncClient
    )

    platform = DiscordPlatform()

    result = await platform.publish("Hello Discord!")

    assert result.status == "success"
    assert result.posted_id == "123456789012345678"
    assert result.channel_id == "987654321098765432"

    assert result.posted_url == (
        "https://discord.com/channels/"
        "111111111111111111/"
        "987654321098765432/"
        "123456789012345678"
    )


@pytest.mark.asyncio
async def test_discord_missing_credentials(monkeypatch):

    monkeypatch.setattr(
        settings,
        "discord_webhook_url",
        None
    )

    platform = DiscordPlatform()

    result = await platform.publish("Hello Discord!")

    assert result.status == "skipped"


@pytest.mark.asyncio
async def test_telegram_success(monkeypatch):

    monkeypatch.setattr(
        settings,
        "telegram_bot_token",
        "test-token"
    )

    monkeypatch.setattr(
        settings,
        "telegram_chat_id",
        "123456789"
    )

    monkeypatch.setattr(
    "app.platforms.telegram.httpx.AsyncClient",
    FakeTelegramAsyncClient
    )

    platform = TelegramPlatform()

    result = await platform.publish("Hello Telegram!")

    assert result.platform == "telegram"
    assert result.status == "success"


@pytest.mark.asyncio
async def test_telegram_missing_credentials(monkeypatch):

    monkeypatch.setattr(
        settings,
        "telegram_bot_token",
        None
    )

    platform = TelegramPlatform()
    result = await platform.publish("Hello Telegram!")

    assert result.status == "skipped"
