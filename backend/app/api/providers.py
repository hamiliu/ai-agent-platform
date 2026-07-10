from fastapi import APIRouter

from app.providers.chat.registry import ChatProviderRegistry
from app.providers.image.registry import ImageProviderRegistry
from app.providers.voice.registry import VoiceProviderRegistry
from app.schemas.schemas import ModelInfo as ModelInfoSchema

router = APIRouter()


def _to_schema(provider_name: str, models) -> list[dict]:
    return [
        {"id": m.id, "name": m.name, "provider": m.provider,
         "capabilities": m.capabilities}
        for m in models
    ]


@router.get("/")
async def list_providers():
    chat_providers = {}
    for name, models in ChatProviderRegistry.list_all().items():
        chat_providers[name] = _to_schema(name, models)

    image_providers = {}
    for name, models in ImageProviderRegistry.list_all().items():
        image_providers[name] = _to_schema(name, models)

    voice_providers = {}
    for name, models in VoiceProviderRegistry.list_all().items():
        voice_providers[name] = _to_schema(name, models)

    return {
        "chat": chat_providers,
        "image": image_providers,
        "voice": voice_providers,
    }
