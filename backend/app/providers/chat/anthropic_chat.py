from typing import AsyncIterator

from anthropic import AsyncAnthropic

from app.providers.base import ChatProvider, ModelInfo


class AnthropicChatProvider(ChatProvider):
    provider_name = "anthropic"

    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    def get_available_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(id="claude-sonnet-4-20250514", name="Claude Sonnet 4",
                      provider="anthropic", capabilities=["chat", "streaming"]),
            ModelInfo(id="claude-3-5-haiku-20241022", name="Claude 3.5 Haiku",
                      provider="anthropic", capabilities=["chat", "streaming"]),
            ModelInfo(id="claude-opus-4-20250514", name="Claude Opus 4",
                      provider="anthropic", capabilities=["chat", "streaming"]),
        ]

    async def chat(self, messages: list[dict], model: str = "claude-sonnet-4-20250514",
                   **kwargs) -> str:
        # Convert OpenAI-style messages to Anthropic format
        system_msg = None
        msgs = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                msgs.append({"role": m["role"], "content": m["content"]})

        create_kwargs = {
            "model": model,
            "messages": msgs,
            "max_tokens": kwargs.get("max_tokens", 4096),
        }
        if system_msg:
            create_kwargs["system"] = system_msg

        resp = await self.client.messages.create(**create_kwargs)
        return resp.content[0].text if resp.content else ""

    async def chat_stream(self, messages: list[dict], model: str = "claude-sonnet-4-20250514",
                          **kwargs) -> AsyncIterator[str]:
        system_msg = None
        msgs = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                msgs.append({"role": m["role"], "content": m["content"]})

        create_kwargs = {
            "model": model,
            "messages": msgs,
            "max_tokens": kwargs.get("max_tokens", 4096),
        }
        if system_msg:
            create_kwargs["system"] = system_msg

        async with self.client.messages.stream(**create_kwargs) as stream:
            async for text in stream.text_stream:
                yield text
