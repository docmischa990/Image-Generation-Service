from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import firebase_admin
from firebase_admin import credentials, storage

from app.config import get_settings


class FirebaseStorageError(Exception):
    """Raised when Firebase Storage initialization or upload fails."""


def initialize_firebase() -> None:
    settings = get_settings()

    if firebase_admin._apps:
        return

    service_account_path = settings.firebase_service_account_path
    if not service_account_path.exists():
        raise FirebaseStorageError(
            f"Firebase service account file not found: {service_account_path}"
        )

    try:
        cred = credentials.Certificate(str(service_account_path))
        firebase_admin.initialize_app(
            cred,
            {"storageBucket": settings.firebase_storage_bucket},
        )
    except Exception as exc:  # pragma: no cover - firebase-admin raises mixed types
        raise FirebaseStorageError("Failed to initialize Firebase Admin SDK") from exc


class FirebaseStorageClient:
    def __init__(self) -> None:
        initialize_firebase()
        self.settings = get_settings()
        self.bucket = storage.bucket()

    def upload_image(self, image_path: Path) -> str:
        blob_path = f"generated-recipes/{uuid4()}.png"
        blob = self.bucket.blob(blob_path)

        try:
            blob.upload_from_filename(str(image_path), content_type="image/png")
            blob.make_public()
        except Exception as exc:  # pragma: no cover - firebase-admin raises mixed types
            raise FirebaseStorageError(
                f"Failed to upload generated image to Firebase: {exc}"
            ) from exc

        return blob.public_url
