
def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_posting_endpoint_success(client, monkeypatch, fake_posting_service):
    monkeypatch.setattr(
        "app.main.posting_service",
        fake_posting_service
    )

    response = client.post(
        "/posting",
        json={"message": "Hello from our system https://example.com"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert len(data["results"]) == 2
    assert data["results"][0]["platform"] == "discord"
    assert data["results"][1]["platform"] == "telegram"


def test_posting_rejects_empty_message(client):
    response = client.post("/posting", json={"message": ""})
    assert response.status_code == 422


def test_posting_rejects_message_over_200_characters(client):
    response = client.post("/posting", json={"message": "A" * 201})
    assert response.status_code == 422


def test_posting_rejects_missing_url(client):
    response = client.post("/posting", json={"message": "Hello everyone"})
    assert response.status_code == 422


def test_posting_rejects_multiple_urls(client):
    response = client.post(
        "/posting",
        json={
            "message": "Visit https://example.com and https://google.com"
        }
    )
    assert response.status_code == 422
