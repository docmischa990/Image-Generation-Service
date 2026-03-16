from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.clients.comfy_client import ComfyUIClient
from app.clients.firebase_storage import FirebaseStorageClient
from app.utils.prompt_builder import build_recipe_image_prompt


class ImageGenerationService:
    def __init__(
        self,
        comfy_client: Optional[ComfyUIClient] = None,
        firebase_client: Optional[FirebaseStorageClient] = None,
    ) -> None:
        self.comfy_client = comfy_client or ComfyUIClient()
        self.firebase_client = firebase_client or FirebaseStorageClient()

    def generate_recipe_image(self, title: str, description: Optional[str]) -> str:
        prompt = build_recipe_image_prompt(title=title, description=description)
        temp_image_path = self.comfy_client.generate_image(prompt)

        try:
            return self.firebase_client.upload_image(temp_image_path)
        finally:
            self._cleanup_temp_file(temp_image_path)

    @staticmethod
    def _cleanup_temp_file(path: Path) -> None:
        if path.exists():
            path.unlink()
