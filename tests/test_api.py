from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app, posting_service
from app.schemas.response import PlatformResult, PostingResponse


client = TestClient(app)


class FakePostingService:

    async def publish(self, message: str) -> PostingResponse:
        return PostingResponse(
            success=True,
            results=[
                PlatformResult(
                    platform="discord",
                    status="success"
                ),
                PlatformResult(
                    platform="telegram",
                    status="success"
                )
            ],
            completed_at=datetime(2026, 11, 16, 12, 0, 0, tzinfo=timezone.utc)
        )


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_posting_endpoint_success(monkeypatch):

    monkeypatch.setattr(
        "app.main.posting_service",
        FakePostingService()
    )

    response = client.post(
        "/posting",
        json={
            "message": "Hello from our system https://example.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert len(data["results"]) == 2
    assert data["results"][0]["platform"] == "discord"
    assert data["results"][1]["platform"] == "telegram"


def test_posting_rejects_empty_message():

    response = client.post(
        "/posting",
        json={"message": ""}
    )

    assert response.status_code == 422


def test_posting_rejects_message_over_200_characters():

    response = client.post(
        "/posting",
        json={
            "message": "A" * 201
        }
    )

    assert response.status_code == 422


def test_posting_rejects_missing_url():

    response = client.post(
        "/posting",
        json={"message": "Hello everyone"}
    )

    assert response.status_code == 422


def test_posting_rejects_multiple_urls():

    response = client.post(
        "/posting",
        json={
            "message": "Visit https://example.com and https://google.com"
        }
    )

    assert response.status_code == 422
