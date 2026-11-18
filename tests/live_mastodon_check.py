import asyncio
import httpx

from app.core.config import settings


async def main():
    instance_url = (settings.mastodon_instance_url or "").rstrip("/")
    access_token = settings.mastodon_access_token

    if not instance_url or not access_token:
        print("Mastodon credentials are missing.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:

        # 1. Verify account credentials
        verify_response = await client.get(
            f"{instance_url}/api/v1/accounts/verify_credentials",
            headers=headers
        )

        print("Credential verification status:", verify_response.status_code)

        if verify_response.is_error:
            print("Verification failed:", verify_response.text)
            return

        account = verify_response.json()
        print("Authenticated account:", account.get("username"))
        print("Account verification successful.")

        # 2. Publish one real test status
        post_response = await client.post(
            f"{instance_url}/api/v1/statuses",
            headers=headers,
            json={
                "status": (
                    "Spent some time outside today and it was exactly what I needed. "
                    "Sometimes a quiet break makes everything feel a little easier."
                ),
                "visibility": "public"
            }
        )

        print("\nPublish status:", post_response.status_code)

        if post_response.is_error:
            print("Publishing failed:", post_response.text)
            return

        data = post_response.json()

        # Print only relevant response fields
        print("\nMastodon API Response:")
        print({
            "id": data.get("id"),
            "url": data.get("url"),
            "uri": data.get("uri"),
            "visibility": data.get("visibility"),
            "created_at": data.get("created_at")
        })


if __name__ == "__main__":
    asyncio.run(main())
