from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Chat ---
class ChatMessage(BaseModel):
    role: str       # user / assistant / system
    content: str


class ChatRequest(BaseModel):
    provider: str = "openai"
    model: str = ""
    messages: list[ChatMessage]
    conversation_id: Optional[str] = None
    temperature: Optional[float] = None


class ChatResponse(BaseModel):
    content: str
    conversation_id: str


# --- Image ---
class TextToImageRequest(BaseModel):
    provider: str = "openai"
    model: str = ""
    prompt: str
    size: str = "1024x1024"


class ImageToImageRequest(BaseModel):
    provider: str = "stability"
    model: str = ""
    prompt: str
    image_file_id: str
    strength: float = 0.8


class ImageResult(BaseModel):
    url: str
    revised_prompt: str = ""
    seed: Optional[int] = None


# --- Voice ---
class VoiceCloneRequest(BaseModel):
    provider: str = "elevenlabs"
    model: str = ""
    text: str
    sample_file_ids: list[str] = []


class VoiceCloneResult(BaseModel):
    audio_url: str


# --- File ---
class FileUploadResult(BaseModel):
    file_id: str
    path: str
    filename: str
    content_type: str
    size: int


# --- Provider ---
class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    capabilities: list[str]


class ProviderListResponse(BaseModel):
    chat: dict[str, list[ModelInfo]]
    image: dict[str, list[ModelInfo]]
    voice: dict[str, list[ModelInfo]]


# --- Conversation List ---
class ConversationSummary(BaseModel):
    id: str
    title: str
    provider: str
    model: str
    created_at: datetime
    message_count: int


class ConversationDetail(BaseModel):
    id: str
    title: str
    provider: str
    model: str
    created_at: datetime
    messages: list[ChatMessage]
