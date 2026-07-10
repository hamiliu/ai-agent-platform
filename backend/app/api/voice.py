from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.schemas import VoiceCloneRequest
from app.services.voice_service import VoiceService
from app.providers.voice.registry import VoiceProviderRegistry

router = APIRouter()


@router.post("/clone")
async def clone_voice(req: VoiceCloneRequest,
                      db: AsyncSession = Depends(get_db)):
    if not VoiceProviderRegistry.is_registered(req.provider):
        raise HTTPException(status_code=400,
                            detail=f"Provider '{req.provider}' not available")
    if not req.sample_file_ids:
        raise HTTPException(status_code=400,
                            detail="At least one audio sample is required")
    try:
        result = await VoiceService.clone_and_speak(
            req.provider, req.text, req.sample_file_ids, req.model,
            db=db,
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
