from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.image import GenerateImageRequest, GenerateImageResponse
from app.services.image_generation import ImageGenerationService

router = APIRouter()


def get_image_generation_service() -> ImageGenerationService:
    return ImageGenerationService()


@router.post("/generate-image", response_model=GenerateImageResponse)
def generate_image(
    payload: GenerateImageRequest,
    service: ImageGenerationService = Depends(get_image_generation_service),
) -> GenerateImageResponse:
    image_url = service.generate_recipe_image(
        title=payload.title,
        description=payload.description,
    )
    return GenerateImageResponse(imageUrl=image_url)
