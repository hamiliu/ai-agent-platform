from typing import AsyncIterator

from openai import AsyncOpenAI

from app.providers.base import ChatProvider, ModelInfo


class OpenAIChatProvider(ChatProvider):
    provider_name = "openai"

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._is_custom_base = "api.openai.com" not in base_url

    def get_available_models(self) -> list[ModelInfo]:
        if self._is_custom_base:
            # 非标准 OpenAI API（如火山引擎 Ark）— 内置常用模型 + 自定义输入
            return [
                ModelInfo(id="doubao-seed-1-6-flash-250615",
                          name="Doubao Seed 1.6 Flash (推荐)",
                          provider="openai",
                          capabilities=["chat", "streaming"]),
                ModelInfo(id="__custom__", name="其他模型 (手动输入模型名)",
                          provider="openai",
                          capabilities=["chat", "streaming", "custom"]),
            ]
        return [
            ModelInfo(id="gpt-4o", name="GPT-4o", provider="openai",
                      capabilities=["chat", "streaming", "vision"]),
            ModelInfo(id="gpt-4o-mini", name="GPT-4o Mini", provider="openai",
                      capabilities=["chat", "streaming"]),
            ModelInfo(id="gpt-4o-turbo", name="GPT-4o Turbo", provider="openai",
                      capabilities=["chat", "streaming"]),
        ]

    async def chat(self, messages: list[dict], model: str = "gpt-4o",
                   **kwargs) -> str:
        resp = await self.client.chat.completions.create(
            model=model, messages=messages, stream=False, **kwargs
        )
        return resp.choices[0].message.content or ""

    async def chat_stream(self, messages: list[dict], model: str = "gpt-4o",
                          **kwargs) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=model, messages=messages, stream=True, **kwargs
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
