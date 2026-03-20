from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from app.clients.comfy_client import ComfyUIClient


def _build_response(
    *,
    json_data: object | None = None,
    content: bytes = b"",
) -> Mock:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = json_data
    response.content = content
    return response


def test_generate_image_with_nested_history_response(tmp_path: Path) -> None:
    client = ComfyUIClient()
    prompt_response = _build_response(json_data={"prompt_id": "test123"})
    history_response = _build_response(
        json_data={
            "test123": {
                "outputs": {
                    "9": {
                        "images": [
                            {
                                "filename": "test.png",
                                "subfolder": "",
                                "type": "output",
                            }
                        ]
                    }
                }
            }
        }
    )
    image_response = _build_response(content=b"fakeimage")

    post_mock = Mock(return_value=prompt_response)
    get_mock = Mock(side_effect=[history_response, image_response])

    client.session.post = post_mock
    client.session.get = get_mock

    image_path = client.generate_image("Spicy Thai Basil Chicken")

    try:
        assert image_path.exists()
        assert image_path.read_bytes() == b"fakeimage"
        post_mock.assert_called_once()
        assert get_mock.call_count == 2
        assert get_mock.call_args_list[0].args[0].endswith("/history/test123")
        assert get_mock.call_args_list[1].args[0].endswith("/view")
        assert get_mock.call_args_list[1].kwargs["params"] == {
            "filename": "test.png",
            "subfolder": "",
            "type": "output",
        }
    finally:
        if image_path.exists():
            image_path.unlink()


def test_generate_image_with_flat_history_response() -> None:
    client = ComfyUIClient()
    prompt_response = _build_response(json_data={"prompt_id": "test123"})
    history_response = _build_response(
        json_data={
            "outputs": {
                "9": {
                    "images": [
                        {
                            "filename": "test.png",
                            "subfolder": "",
                            "type": "output",
                        }
                    ]
                }
            }
        }
    )
    image_response = _build_response(content=b"fakeimage")

    client.session.post = Mock(return_value=prompt_response)
    client.session.get = Mock(side_effect=[history_response, image_response])

    image_path = client.generate_image("Spicy Thai Basil Chicken")

    try:
        assert image_path.exists()
        assert image_path.read_bytes() == b"fakeimage"
    finally:
        if image_path.exists():
            image_path.unlink()
