from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from app.clients.firebase_storage import (
    FirebaseStorageClient,
    FirebaseStorageError,
    initialize_firebase,
)


def test_initialize_firebase_raises_when_service_account_is_missing(
    monkeypatch,
) -> None:
    with patch("app.clients.firebase_storage.firebase_admin._apps", []):
        monkeypatch.setenv(
            "FIREBASE_SERVICE_ACCOUNT_PATH",
            "config/does-not-exist.json",
        )
        from app.config import get_settings

        get_settings.cache_clear()
        try:
            try:
                initialize_firebase()
            except FirebaseStorageError as exc:
                assert "Firebase service account file not found" in str(exc)
            else:
                raise AssertionError("Expected FirebaseStorageError")
        finally:
            get_settings.cache_clear()


def test_upload_image_raises_original_firebase_error_message(tmp_path: Path) -> None:
    image_path = tmp_path / "generated.png"
    image_path.write_bytes(b"image-bytes")

    blob = Mock()
    blob.upload_from_filename.side_effect = RuntimeError("storage quota exceeded")
    bucket = Mock()
    bucket.blob.return_value = blob

    with patch("app.clients.firebase_storage.initialize_firebase"):
        with patch("app.clients.firebase_storage.storage.bucket", return_value=bucket):
            client = FirebaseStorageClient()

    try:
        client.upload_image(image_path)
    except FirebaseStorageError as exc:
        assert str(exc) == (
            "Failed to upload generated image to Firebase: storage quota exceeded"
        )
    else:
        raise AssertionError("Expected FirebaseStorageError")


def test_upload_image_returns_public_url(tmp_path: Path) -> None:
    image_path = tmp_path / "generated.png"
    image_path.write_bytes(b"image-bytes")

    blob = Mock()
    blob.public_url = "https://storage.googleapis.com/generated/image.png"
    bucket = Mock()
    bucket.blob.return_value = blob

    with patch("app.clients.firebase_storage.initialize_firebase"):
        with patch("app.clients.firebase_storage.storage.bucket", return_value=bucket):
            client = FirebaseStorageClient()

    image_url = client.upload_image(image_path)

    assert image_url == "https://storage.googleapis.com/generated/image.png"
    blob.upload_from_filename.assert_called_once_with(
        str(image_path),
        content_type="image/png",
    )
    blob.make_public.assert_called_once()
