from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict


load_dotenv()


class Settings(BaseModel):
    comfyui_url: str
    firebase_storage_bucket: str
    firebase_service_account_path: Path = Path("config/firebase_service_account.json")
    comfyui_request_timeout_seconds: int = 30
    comfyui_generation_timeout_seconds: int = 180
    comfyui_poll_interval_seconds: int = 2
    comfyui_checkpoint_name: str = "sd_xl_base_1.0.safetensors"
    comfyui_width: int = 1024
    comfyui_height: int = 1024
    comfyui_steps: int = 30
    comfyui_cfg: float = 7.0

    model_config = ConfigDict(frozen=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        comfyui_url=os.environ["COMFYUI_URL"],
        firebase_storage_bucket=os.environ["FIREBASE_STORAGE_BUCKET"],
        firebase_service_account_path=Path(
            os.getenv(
                "FIREBASE_SERVICE_ACCOUNT_PATH",
                "config/firebase_service_account.json",
            )
        ),
        comfyui_request_timeout_seconds=int(
            os.getenv("COMFYUI_REQUEST_TIMEOUT_SECONDS", "30")
        ),
        comfyui_generation_timeout_seconds=int(
            os.getenv("COMFYUI_GENERATION_TIMEOUT_SECONDS", "180")
        ),
        comfyui_poll_interval_seconds=int(
            os.getenv("COMFYUI_POLL_INTERVAL_SECONDS", "2")
        ),
        comfyui_checkpoint_name=os.getenv(
            "COMFYUI_CHECKPOINT_NAME",
            "sd_xl_base_1.0.safetensors",
        ),
        comfyui_width=int(os.getenv("COMFYUI_WIDTH", "1024")),
        comfyui_height=int(os.getenv("COMFYUI_HEIGHT", "1024")),
        comfyui_steps=int(os.getenv("COMFYUI_STEPS", "30")),
        comfyui_cfg=float(os.getenv("COMFYUI_CFG", "7.0")),
    )
