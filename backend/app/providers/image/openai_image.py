from openai import AsyncOpenAI

from app.providers.base import ImageProvider, ModelInfo


class OpenAIImageProvider(ImageProvider):
    provider_name = "openai"

    def __init__(self, api_key: str):
        # DALL-E only works on the official OpenAI API
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://api.openai.com/v1")

    def get_available_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(id="gpt-image-1", name="GPT Image 1", provider="openai",
                      capabilities=["text-to-image"]),
            ModelInfo(id="gpt-image-1-mini", name="GPT Image 1 Mini", provider="openai",
                      capabilities=["text-to-image"]),
            ModelInfo(id="gpt-image-1.5", name="GPT Image 1.5", provider="openai",
                      capabilities=["text-to-image"]),
            ModelInfo(id="gpt-image-2", name="GPT Image 2", provider="openai",
                      capabilities=["text-to-image"]),
        ]

    async def text_to_image(self, prompt: str, model: str = "gpt-image-1",
                            **kwargs) -> tuple[bytes, str]:
        size = kwargs.get("size", "1024x1024")
        resp = await self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            n=1,
        )
        img_data = resp.data[0]
        # Download the image from the URL
        import httpx
        async with httpx.AsyncClient() as client:
            r = await client.get(img_data.url, timeout=30)
            r.raise_for_status()
            image_bytes = r.content
        revised = img_data.revised_prompt or prompt
        return image_bytes, revised

    async def image_to_image(self, prompt: str, image_bytes: bytes,
                             model: str = "", **kwargs) -> tuple[bytes, str]:
        # DALL-E 3 doesn't support image-to-image directly.
        # For OpenAI, we return the original image with a note.
        # Stability provider handles actual img2img.
        raise NotImplementedError(
            "OpenAI DALL-E does not support image-to-image. Use the Stability provider."
        )
