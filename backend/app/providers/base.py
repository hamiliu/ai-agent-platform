from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Optional


@dataclass
class ModelInfo:
    id: str
    name: str
    provider: str
    capabilities: list[str]


# ─── Chat Provider ────────────────────────────────────────────────

class ChatProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    def get_available_models(self) -> list[ModelInfo]: ...

    @abstractmethod
    async def chat(
        self, messages: list[dict], model: str = "", **kwargs
    ) -> str: ...

    @abstractmethod
    async def chat_stream(
        self, messages: list[dict], model: str = "", **kwargs
    ) -> AsyncIterator[str]: ...


# ─── Image Provider ───────────────────────────────────────────────

class ImageProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    def get_available_models(self) -> list[ModelInfo]: ...

    @abstractmethod
    async def text_to_image(
        self, prompt: str, model: str = "", **kwargs
    ) -> tuple[bytes, str]: ...      # (image_bytes, revised_prompt)

    @abstractmethod
    async def image_to_image(
        self, prompt: str, image_bytes: bytes, model: str = "", **kwargs
    ) -> tuple[bytes, str]: ...      # (image_bytes, revised_prompt)


# ─── Voice Provider ───────────────────────────────────────────────

class VoiceProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    def get_available_models(self) -> list[ModelInfo]: ...

    @abstractmethod
    async def clone_and_speak(
        self, audio_samples: list[bytes], text: str, **kwargs
    ) -> bytes: ...

    @abstractmethod
    async def text_to_speech(
        self, text: str, voice_id: str = "", **kwargs
    ) -> bytes: ...
