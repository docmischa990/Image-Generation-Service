from __future__ import annotations

from typing import Optional


def build_recipe_image_prompt(title: str, description: Optional[str] = None) -> str:
    parts = [f"Professional food photography of {title}."]

    if description:
        parts.append(f"{description}.")

    parts.append(
        "Studio lighting, high detail, shallow depth of field, 85mm lens, realistic textures."
    )
    return " ".join(parts)
