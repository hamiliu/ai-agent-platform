import os
import httpx
from fastapi import UploadFile

from app.config import settings


def _supabase_storage_url() -> str:
    return f"{settings.SUPABASE_URL}/storage/v1"


def _auth_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apiKey": settings.SUPABASE_SERVICE_KEY,
    }


async def save_upload(file_id: str, file: UploadFile) -> str:
    """Upload a file to Supabase Storage and return the public URL."""
    ext = os.path.splitext(file.filename or "file")[1] or ".bin"
    storage_path = f"{file_id}{ext}"
    content = await file.read()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_supabase_storage_url()}/object/{settings.SUPABASE_STORAGE_BUCKET}/{storage_path}",
            headers=_auth_headers(),
            content=content,
            params={"upsert": "true"},
        )
        resp.raise_for_status()

    return f"{_supabase_storage_url()}/object/public/{settings.SUPABASE_STORAGE_BUCKET}/{storage_path}"


async def get_file_bytes(file_id: str) -> bytes | None:
    """Download file bytes from Supabase Storage by file_id (without extension)."""
    common_exts = [".png", ".jpg", ".jpeg", ".webp", ".mp3", ".wav", ".ogg", ".bin"]
    async with httpx.AsyncClient() as client:
        for ext in common_exts:
            path = f"{file_id}{ext}"
            resp = await client.get(
                f"{_supabase_storage_url()}/object/{settings.SUPABASE_STORAGE_BUCKET}/{path}",
                headers=_auth_headers(),
            )
            if resp.status_code == 200:
                return resp.content
    return None


async def upload_bytes(data: bytes, filename: str) -> str:
    """Upload raw bytes to Supabase Storage and return the public URL."""
    storage_path = filename
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_supabase_storage_url()}/object/{settings.SUPABASE_STORAGE_BUCKET}/{storage_path}",
            headers=_auth_headers(),
            content=data,
            params={"upsert": "true"},
        )
        resp.raise_for_status()

    return f"{_supabase_storage_url()}/object/public/{settings.SUPABASE_STORAGE_BUCKET}/{storage_path}"
