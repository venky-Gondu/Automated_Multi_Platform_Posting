
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Discord
    discord_webhook_url: str | None = None
    discord_guild_id: str | None = None

    # Telegram
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    # Mastodon
    mastodon_instance_url: str | None = None
    mastodon_access_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
