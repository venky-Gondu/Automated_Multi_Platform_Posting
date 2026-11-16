
import httpx

from app.core.config import settings
from app.platforms.base import BasePlatform
from app.schemas.response import PlatformResult


class TelegramPlatform(BasePlatform):

    @property
    def name(self) -> str:
        return "telegram"

    @property
    def is_configured(self) -> bool:
        return bool(
            settings.telegram_bot_token
            and settings.telegram_chat_id
        )

    async def publish(self, message: str) -> PlatformResult:

        bot_token = settings.telegram_bot_token
        chat_id = settings.telegram_chat_id

        if not bot_token or not chat_id:
            return PlatformResult(
                platform=self.name,
                status="skipped",
                error="Telegram credentials are not configured."
            )

        api_url = (
            f"https://api.telegram.org/bot{bot_token}/sendMessage"
        )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:

                response = await client.post(
                    api_url,
                    json={
                        "chat_id": chat_id,
                        "text": message
                    }
                )

                response.raise_for_status()
                data = response.json()

                if not data.get("ok"):
                    return PlatformResult(
                        platform=self.name,
                        status="failed",
                        error="Telegram rejected the message."
                    )

                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=None,
                    public_access=None
                )

        except httpx.TimeoutException:
            error = "Telegram request timed out."

        except httpx.HTTPStatusError as exc:
            error = f"Telegram API returned HTTP {exc.response.status_code}."

        except httpx.RequestError:
            error = "Unable to connect to Telegram."

        except ValueError:
            error = "Telegram returned an invalid response."

        return PlatformResult(
            platform=self.name,
            status="failed",
            error=error
        )
