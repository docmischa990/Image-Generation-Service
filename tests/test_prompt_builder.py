from app.utils.prompt_builder import build_recipe_image_prompt


def test_build_prompt_with_description() -> None:
    prompt = build_recipe_image_prompt(
        title="Spicy Thai Basil Chicken",
        description="A quick stir fry with garlic, chilies and basil",
    )

    assert (
        prompt
        == "Professional food photography of Spicy Thai Basil Chicken. "
        "A quick stir fry with garlic, chilies and basil. "
        "Studio lighting, high detail, shallow depth of field, 85mm lens, realistic textures."
    )


def test_build_prompt_without_description() -> None:
    prompt = build_recipe_image_prompt(title="Spicy Thai Basil Chicken")

    assert (
        prompt
        == "Professional food photography of Spicy Thai Basil Chicken. "
        "Studio lighting, high detail, shallow depth of field, 85mm lens, realistic textures."
    )
