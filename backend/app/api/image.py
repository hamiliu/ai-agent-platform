from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.schemas import TextToImageRequest, ImageToImageRequest
from app.services.image_service import ImageService
from app.providers.image.registry import ImageProviderRegistry

router = APIRouter()


@router.post("/text-to-image")
async def text_to_image(req: TextToImageRequest,
                        db: AsyncSession = Depends(get_db)):
    if not ImageProviderRegistry.is_registered(req.provider):
        raise HTTPException(status_code=400,
                            detail=f"Provider '{req.provider}' not available")
    try:
        result = await ImageService.generate_text_to_image(
            req.provider, req.prompt, req.model,
            db=db, size=req.size,
        )
        return result
    except NotImplementedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-to-image")
async def image_to_image(req: ImageToImageRequest,
                         db: AsyncSession = Depends(get_db)):
    if not ImageProviderRegistry.is_registered(req.provider):
        raise HTTPException(status_code=400,
                            detail=f"Provider '{req.provider}' not available")
    try:
        result = await ImageService.generate_image_to_image(
            req.provider, req.prompt, req.image_file_id, req.model,
            db=db, strength=req.strength,
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
