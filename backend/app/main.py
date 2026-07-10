import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db


def _register_providers():
    """Initialize and register all providers that have API keys configured."""
    from app.providers.chat.registry import ChatProviderRegistry
    from app.providers.chat.openai_chat import OpenAIChatProvider
    from app.providers.chat.anthropic_chat import AnthropicChatProvider

    from app.providers.image.registry import ImageProviderRegistry
    from app.providers.image.openai_image import OpenAIImageProvider
    from app.providers.image.stability_image import StabilityImageProvider

    from app.providers.voice.registry import VoiceProviderRegistry
    from app.providers.voice.elevenlabs_voice import ElevenLabsVoiceProvider

    # Chat providers
    if settings.OPENAI_API_KEY:
        ChatProviderRegistry.register(
            OpenAIChatProvider(settings.OPENAI_API_KEY, settings.OPENAI_BASE_URL)
        )
    if settings.ANTHROPIC_API_KEY:
        ChatProviderRegistry.register(
            AnthropicChatProvider(settings.ANTHROPIC_API_KEY)
        )

    # Image providers
    if settings.OPENAI_IMAGE_API_KEY:
        ImageProviderRegistry.register(
            OpenAIImageProvider(settings.OPENAI_IMAGE_API_KEY)
        )
    if settings.STABILITY_API_KEY:
        ImageProviderRegistry.register(
            StabilityImageProvider(settings.STABILITY_API_KEY)
        )

    # Voice providers
    if settings.ELEVENLABS_API_KEY:
        VoiceProviderRegistry.register(
            ElevenLabsVoiceProvider(settings.ELEVENLABS_API_KEY)
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    _register_providers()
    yield
    # Shutdown — nothing to clean up


app = FastAPI(
    title="AI Agent Platform",
    description="A Coze-like AI agent platform with chat, image generation, and voice cloning.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow configured origins
allowed_origins = json.loads(settings.CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
from app.api import chat, image, voice, files, providers
app.include_router(chat.router, prefix="/api/chat")
app.include_router(image.router, prefix="/api/images")
app.include_router(voice.router, prefix="/api/voice")
app.include_router(files.router, prefix="/api/files")
app.include_router(providers.router, prefix="/api/providers")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
