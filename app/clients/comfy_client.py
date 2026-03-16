from __future__ import annotations

import copy
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

import requests

from app.config import get_settings


class ComfyUIError(Exception):
    """Raised when the ComfyUI workflow fails or returns an invalid result."""


class ComfyUITimeoutError(ComfyUIError):
    """Raised when image generation exceeds the configured timeout."""


class ComfyUIClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.comfyui_url.rstrip("/")
        self.session = requests.Session()

    def generate_image(self, prompt: str) -> Path:
        prompt_id = self._queue_prompt(prompt)
        image_metadata = self._wait_for_image(prompt_id)
        return self._download_image(image_metadata)

    def _queue_prompt(self, prompt: str) -> str:
        workflow = self._build_workflow(prompt)
        response = self.session.post(
            f"{self.base_url}/prompt",
            json={"prompt": workflow, "client_id": str(uuid4())},
            timeout=self.settings.comfyui_request_timeout_seconds,
        )
        self._raise_for_status(response, "Failed to queue ComfyUI prompt")

        data = response.json()
        prompt_id = data.get("prompt_id")
        if not prompt_id:
            raise ComfyUIError("ComfyUI response did not include a prompt_id")
        return prompt_id

    def _wait_for_image(self, prompt_id: str) -> dict[str, str]:
        deadline = time.monotonic() + self.settings.comfyui_generation_timeout_seconds

        while time.monotonic() < deadline:
            response = self.session.get(
                f"{self.base_url}/history/{prompt_id}",
                timeout=self.settings.comfyui_request_timeout_seconds,
            )
            self._raise_for_status(response, "Failed to fetch ComfyUI history")

            history = response.json().get(prompt_id)
            if history:
                return self._extract_image_metadata(history)

            time.sleep(self.settings.comfyui_poll_interval_seconds)

        raise ComfyUITimeoutError("Timed out waiting for ComfyUI image generation")

    def _extract_image_metadata(self, history: dict[str, Any]) -> dict[str, str]:
        outputs = history.get("outputs", {})
        for node_output in outputs.values():
            images = node_output.get("images") or []
            if images:
                image = images[0]
                filename = image.get("filename")
                if not filename:
                    break
                return {
                    "filename": filename,
                    "subfolder": image.get("subfolder", ""),
                    "type": image.get("type", "output"),
                }
        raise ComfyUIError("ComfyUI completed without returning an image output")

    def _download_image(self, image_metadata: dict[str, str]) -> Path:
        response = self.session.get(
            f"{self.base_url}/view",
            params=image_metadata,
            timeout=self.settings.comfyui_request_timeout_seconds,
        )
        self._raise_for_status(response, "Failed to download generated image")

        temp_path = Path("/tmp") / f"{uuid4()}.png"
        temp_path.write_bytes(response.content)
        return temp_path

    def _build_workflow(self, prompt: str) -> dict[str, dict[str, Any]]:
        workflow = copy.deepcopy(SDXL_WORKFLOW_TEMPLATE)
        workflow["3"]["inputs"]["text"] = prompt
        workflow["4"]["inputs"]["ckpt_name"] = self.settings.comfyui_checkpoint_name
        workflow["5"]["inputs"]["width"] = self.settings.comfyui_width
        workflow["5"]["inputs"]["height"] = self.settings.comfyui_height
        workflow["5"]["inputs"]["batch_size"] = 1
        workflow["6"]["inputs"]["seed"] = uuid4().int % (2**32)
        workflow["6"]["inputs"]["steps"] = self.settings.comfyui_steps
        workflow["6"]["inputs"]["cfg"] = self.settings.comfyui_cfg
        return workflow

    @staticmethod
    def _raise_for_status(response: requests.Response, message: str) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ComfyUIError(f"{message}: {response.text}") from exc


SDXL_WORKFLOW_TEMPLATE: dict[str, dict[str, Any]] = {
    "3": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "",
            "clip": ["4", 1],
        },
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": "sd_xl_base_1.0.safetensors",
        },
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "width": 1024,
            "height": 1024,
            "batch_size": 1,
        },
    },
    "6": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 1,
            "steps": 30,
            "cfg": 7.0,
            "sampler_name": "dpmpp_2m",
            "scheduler": "karras",
            "denoise": 1,
            "model": ["4", 0],
            "positive": ["3", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0],
        },
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "blurry, noisy, distorted, deformed, text, watermark",
            "clip": ["4", 1],
        },
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": ["6", 0],
            "vae": ["4", 2],
        },
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "recipe",
            "images": ["8", 0],
        },
    },
}
