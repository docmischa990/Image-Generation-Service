from pathlib import Path

from app.clients.comfy_client import ComfyUITimeoutError
from app.clients.firebase_storage import FirebaseStorageError
from app.services.image_generation import ImageGenerationService


class StubComfyClient:
    def __init__(self, path: Path) -> None:
        self.path = path

    def generate_image(self, prompt: str) -> Path:
        assert "Professional food photography of Spicy Thai Basil Chicken." in prompt
        return self.path


class StubFirebaseClient:
    def upload_image(self, image_path: Path) -> str:
        assert image_path.exists()
        return "https://storage.googleapis.com/generated/image.png"


class FailingFirebaseClient:
    def upload_image(self, image_path: Path) -> str:
        raise FirebaseStorageError("upload failed")


def test_service_generates_and_uploads_image(tmp_path: Path) -> None:
    image_path = tmp_path / "generated.png"
    image_path.write_bytes(b"image-bytes")

    service = ImageGenerationService(
        comfy_client=StubComfyClient(image_path),
        firebase_client=StubFirebaseClient(),
    )

    image_url = service.generate_recipe_image(
        title="Spicy Thai Basil Chicken",
        description="A quick stir fry with garlic, chilies and basil",
    )

    assert image_url == "https://storage.googleapis.com/generated/image.png"
    assert not image_path.exists()


def test_service_cleans_up_file_on_upload_failure(tmp_path: Path) -> None:
    image_path = tmp_path / "generated.png"
    image_path.write_bytes(b"image-bytes")

    service = ImageGenerationService(
        comfy_client=StubComfyClient(image_path),
        firebase_client=FailingFirebaseClient(),
    )

    try:
        service.generate_recipe_image(
            title="Spicy Thai Basil Chicken",
            description=None,
        )
    except FirebaseStorageError as exc:
        assert str(exc) == "upload failed"
    else:
        raise AssertionError("Expected FirebaseStorageError")

    assert not image_path.exists()


def test_timeout_error_propagates(tmp_path: Path) -> None:
    class TimeoutComfyClient:
        def generate_image(self, prompt: str) -> Path:
            raise ComfyUITimeoutError("timeout")

    service = ImageGenerationService(
        comfy_client=TimeoutComfyClient(),
        firebase_client=StubFirebaseClient(),
    )

    try:
        service.generate_recipe_image("Spicy Thai Basil Chicken", None)
    except ComfyUITimeoutError as exc:
        assert str(exc) == "timeout"
    else:
        raise AssertionError("Expected ComfyUITimeoutError")
