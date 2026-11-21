import os

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

os.environ["JWT_SECRET"] = "test-only-secret"

from api.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_token_and_recommendations(client):
    token_response = client.post("/auth/token")
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]

    response = client.get(
        "/recommendations/999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (200, 503)


def test_recommendation_requires_token(client):
    response = client.get("/recommendations/1")
    assert response.status_code == 401


def test_invalid_user_id(client):
    token_response = client.post("/auth/token")
    token = token_response.json()["access_token"]
    response = client.get(
        "/recommendations/0",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


def test_publish_user_interaction(client):
    token_response = client.post("/auth/token")
    token = token_response.json()["access_token"]

    with patch(
        "api.main.publish_event",
        new=AsyncMock(),
    ):
        response = client.post(
            "/events/user-interaction",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_id": 1,
                "product_id": 3868,
                "interaction": "recommendation_requested",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["published"] is True
    assert body["event_type"] == "user.interaction"

