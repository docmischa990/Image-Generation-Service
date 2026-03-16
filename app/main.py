from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import router as image_router
from app.clients.comfy_client import ComfyUIError, ComfyUITimeoutError
from app.clients.firebase_storage import FirebaseStorageError, initialize_firebase


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_firebase()
    yield


app = FastAPI(
    title="Image Generation Service",
    description="FastAPI backend for recipe image generation with ComfyUI and Firebase Storage.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(image_router)


@app.exception_handler(ComfyUITimeoutError)
async def handle_comfyui_timeout(_, exc: ComfyUITimeoutError) -> JSONResponse:
    return JSONResponse(status_code=504, content={"detail": str(exc)})


@app.exception_handler(ComfyUIError)
async def handle_comfyui_error(_, exc: ComfyUIError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(FirebaseStorageError)
async def handle_firebase_error(_, exc: FirebaseStorageError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})
