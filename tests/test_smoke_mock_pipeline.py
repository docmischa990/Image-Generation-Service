from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from tests.mock_comfyui_app import app as mock_comfyui_app


class StubFirebaseStorageClient:
    def upload_image(self, image_path: Path) -> str:
        assert image_path.exists()
        assert image_path.read_bytes() == b"fakeimage"
        return "https://storage.googleapis.com/generated/mock-image.png"


class MockResponseAdapter:
    def __init__(self, response) -> None:
        self._response = response
        self.content = response.content
        self.text = response.text

    def json(self):
        return self._response.json()

    def raise_for_status(self) -> None:
        self._response.raise_for_status()


class MockComfyUISession:
    def __init__(self, client: TestClient) -> None:
        self.client = client

    def post(self, url: str, json: dict, timeout: int) -> MockResponseAdapter:
        response = self.client.post(_extract_path(url), json=json)
        return MockResponseAdapter(response)

    def get(
        self,
        url: str,
        params: dict | None = None,
        timeout: int | None = None,
    ) -> MockResponseAdapter:
        response = self.client.get(_extract_path(url), params=params)
        return MockResponseAdapter(response)


def _extract_path(url: str) -> str:
    if "://" not in url:
        return url

    return "/" + url.split("://", maxsplit=1)[1].split("/", maxsplit=1)[1]


def test_generate_image_against_mock_comfyui() -> None:
    with TestClient(mock_comfyui_app) as mock_client:
        with patch("app.clients.comfy_client.requests.Session") as session_factory:
            session_factory.return_value = MockComfyUISession(mock_client)
            with patch("app.main.initialize_firebase"):
                with patch(
                    "app.services.image_generation.FirebaseStorageClient",
                    StubFirebaseStorageClient,
                ):
                    with TestClient(app) as client:
                        response = client.post(
                            "/generate-image",
                            json={
                                "title": "Spicy Thai Basil Chicken",
                                "description": "A quick stir fry with garlic, chilies and basil",
                            },
                        )

    assert response.status_code == 200
    assert response.json() == {
        "imageUrl": "https://storage.googleapis.com/generated/mock-image.png"
    }
