
import re

from pydantic import BaseModel, Field, field_validator


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
        urls = re.findall(r"https?://[^\s]+", value)

        if len(urls) != 1:
            raise ValueError("Message must contain exactly one CTA URL.")

        return value
