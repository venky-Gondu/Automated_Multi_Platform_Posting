
import httpx

from app.core.config import settings
from app.platforms.base import BasePlatform
from app.schemas.response import PlatformResult


class DiscordPlatform(BasePlatform):

    @property
    def name(self) -> str:
        return "discord"

    @property
    def is_configured(self) -> bool:
        return bool(settings.discord_webhook_url)

    async def publish(self, message: str) -> PlatformResult:

        webhook_url = settings.discord_webhook_url

        if not webhook_url:
            return PlatformResult(
                platform=self.name,
                status="skipped",
                error="Discord webhook is not configured."
            )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:

                response = await client.post(
                    webhook_url,
                    params={"wait": "true"},
                    json={"content": message}
                )

                response.raise_for_status()

                return PlatformResult(
                    platform=self.name,
                    status="success"
                )

        except httpx.TimeoutException:
            error = "Discord request timed out."

        except httpx.HTTPStatusError as exc:
            error = f"Discord API returned HTTP {exc.response.status_code}."

        except httpx.RequestError:
            error = "Unable to connect to Discord."

        except ValueError:
            error = "Discord returned an invalid response."

        return PlatformResult(
            platform=self.name,
            status="failed",
            error=error
        )
