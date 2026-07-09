import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.utils.file_storage import save_upload

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_id = str(uuid.uuid4())
    public_url = await save_upload(file_id, file)

    return {
        "file_id": file_id,
        "url": public_url,
        "filename": file.filename,
        "content_type": file.content_type or "application/octet-stream",
    }
