
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
                data = response.json()

                if not isinstance(data, dict):
                    raise ValueError("Invalid Discord response.")

                message_id = data.get("id")
                channel_id = data.get("channel_id")
                guild_id = data.get("guild_id")

                # Discord must return a message ID to confirm creation.
                if not message_id or not channel_id:
                    return PlatformResult(
                        platform=self.name,
                        status="failed",
                        error="Discord did not return message identifiers."
                    )

                # A direct permalink requires the guild, channel and message IDs.
                posted_url = None

                if guild_id:
                    posted_url = (
                        f"https://discord.com/channels/"
                        f"{guild_id}/{channel_id}/{message_id}"
                    )

                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_id=str(message_id),
                    channel_id=str(channel_id),
                    posted_url=posted_url,
                    public_access=None
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
