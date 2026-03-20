# Image Generation Service

Python FastAPI backend for generating recipe images with Stable Diffusion XL through a remote ComfyUI server, then uploading the result to Firebase Storage.

## Requirements

- Python 3.11+
- A reachable ComfyUI server running SDXL
- A Firebase service account JSON with access to the target storage bucket

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the project root:

```env
COMFYUI_URL=http://GPU-IP:8188
FIREBASE_STORAGE_BUCKET=stratus-spoon-v2.appspot.com
FIREBASE_SERVICE_ACCOUNT_PATH=config/firebase_service_account.json
CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
COMFYUI_CHECKPOINT_NAME=sd_xl_base_1.0.safetensors
```

Place your Firebase service account file at `config/firebase_service_account.json`.

## Run Locally

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger docs are available at `http://127.0.0.1:8000/docs`.

## API

`POST /generate-image`

Request body:

```json
{
  "title": "Spicy Thai Basil Chicken",
  "description": "A quick stir fry with garlic, chilies and basil"
}
```

Successful response:

```json
{
  "imageUrl": "https://storage.googleapis.com/..."
}
```

## Notes

- The service generates the image through ComfyUI, stores the temporary file under `/tmp`, uploads it to Firebase Storage, and then deletes the local file.
- Cross-origin browser access is controlled by `CORS_ALLOW_ORIGINS` as a comma-separated list of allowed frontend origins.
- `.env` and `config/firebase_service_account.json` are intentionally ignored by Git.


