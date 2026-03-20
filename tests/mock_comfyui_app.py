from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()


@app.post("/prompt")
async def queue_prompt() -> dict[str, str]:
    return {"prompt_id": "test123"}


@app.get("/history/test123")
async def prompt_history() -> dict[str, object]:
    return {
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


@app.get("/view")
async def view_image() -> Response:
    return Response(content=b"fakeimage", media_type="image/png")
