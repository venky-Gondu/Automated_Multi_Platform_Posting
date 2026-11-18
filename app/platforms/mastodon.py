
import httpx

from datetime import datetime

from app.core.config import settings
from app.platforms.base import BasePlatform
from app.schemas.response import PlatformResult


class MastodonPlatform(BasePlatform):

    @property
    def name(self) -> str:
        return "mastodon"

    @property
    def is_configured(self) -> bool:
        return bool(
            settings.mastodon_instance_url
            and settings.mastodon_access_token
        )

    async def publish(self, message: str) -> PlatformResult:
        instance_url = settings.mastodon_instance_url
        access_token = settings.mastodon_access_token

        if not instance_url or not access_token:
            return PlatformResult(
                platform=self.name,
                status="skipped",
                error="Mastodon credentials are not configured."
            )

        api_url = (
            f"{instance_url.rstrip('/')}/api/v1/statuses"
        )

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json={
                        "status": message,
                        "visibility": "public"
                    }
                )

                response.raise_for_status()
                data = response.json()

                if not isinstance(data, dict):
                    raise ValueError("Invalid Mastodon response.")

                posted_url = data.get("url")

                if not data.get("id"):
                    raise ValueError("Mastodon returned no status ID.")

                posted_at = None
                created_at = data.get("created_at")

                if created_at:
                    posted_at = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )

                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=posted_url,
                    public_access=None,
                    posted_at=posted_at
                )

        except httpx.TimeoutException:
            error = "Mastodon request timed out."

        except httpx.HTTPStatusError as exc:
            error = (
                f"Mastodon API returned HTTP "
                f"{exc.response.status_code}."
            )

        except httpx.RequestError:
            error = "Unable to connect to Mastodon."

        except (ValueError, TypeError, AttributeError):
            error = "Mastodon returned an invalid response."

        return PlatformResult(
            platform=self.name,
            status="failed",
            error=error
        )
