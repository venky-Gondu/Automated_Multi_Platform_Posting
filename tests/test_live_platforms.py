
import asyncio

from app.platforms.discord import DiscordPlatform
from app.platforms.telegram import TelegramPlatform


async def main():

    message = "Hello! This is a real API integration test from our Automated Posting System."

    platforms = [
        DiscordPlatform(),
        TelegramPlatform()
    ]

    for platform in platforms:

        print(f"\nTesting {platform.name}...")

        if not platform.is_configured:
            print("SKIPPED: Credentials are missing.")
            continue

        result = await platform.publish(message)

        print(f"Platform: {result.platform}")
        print(f"Status: {result.status}")

        if result.error:
            print(f"Error: {result.error}")

        if result.status == "success":
            print("Message accepted by the platform API.")


if __name__ == "__main__":
    asyncio.run(main())
