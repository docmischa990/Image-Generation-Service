from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.routes import get_image_generation_service
from app.main import app
from typing import Optional


class StubService:
    def generate_recipe_image(self, title: str, description: Optional[str]) -> str:
        assert title == "Spicy Thai Basil Chicken"
        assert description == "A quick stir fry with garlic, chilies and basil"
        return "https://storage.googleapis.com/generated/image.png"


def test_generate_image_success() -> None:
    app.dependency_overrides[get_image_generation_service] = lambda: StubService()
    with patch("app.main.initialize_firebase"):
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
        "imageUrl": "https://storage.googleapis.com/generated/image.png"
    }
    app.dependency_overrides.clear()


def test_generate_image_validation_error() -> None:
    with patch("app.main.initialize_firebase"):
        with TestClient(app) as client:
            response = client.post(
                "/generate-image",
                json={"title": "   "},
            )

    assert response.status_code == 422
