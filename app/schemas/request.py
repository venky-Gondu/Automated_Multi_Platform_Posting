
import re
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, field_validator


URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


def extract_urls(message: str) -> list[str]:
    urls = URL_PATTERN.findall(message)

    # Remove punctuation commonly placed after URLs in sentences.
    return [
        url.rstrip(".,!?;:")
        for url in urls
    ]


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)

        if parsed.scheme.lower() not in ("http", "https"):
            return False

        if not parsed.hostname:
            return False

        # Do not accept URLs containing embedded credentials.
        if parsed.username or parsed.password:
            return False

        # Accessing port also validates its numeric range.
        if parsed.port is not None and not 1 <= parsed.port <= 65535:
            return False

        return True

    except ValueError:
        return False


class PostingRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Message containing exactly one CTA URL."
    )

    @field_validator("message")
    @classmethod
    def validate_cta_url(cls, value: str) -> str:
        urls = extract_urls(value)

        if len(urls) != 1:
            raise ValueError(
                "Message must contain exactly one CTA URL."
            )

        if not is_valid_url(urls[0]):
            raise ValueError("Message contains an invalid URL.")

        return value
