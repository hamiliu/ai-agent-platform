import httpx

from app.providers.base import ImageProvider, ModelInfo


class StabilityImageProvider(ImageProvider):
    provider_name = "stability"
    BASE_URL = "https://api.stability.ai/v2beta"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _headers(self) -> dict:
        return {
            "authorization": f"Bearer {self.api_key}",
            "accept": "image/*",
        }

    def get_available_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(id="stable-image-core", name="Stable Image Core",
                      provider="stability",
                      capabilities=["text-to-image", "image-to-image"]),
            ModelInfo(id="stable-image-ultra", name="Stable Image Ultra",
                      provider="stability",
                      capabilities=["text-to-image"]),
        ]

    async def text_to_image(self, prompt: str, model: str = "stable-image-core",
                            **kwargs) -> tuple[bytes, str]:
        url = f"{self.BASE_URL}/stable-image/generate/core"
        if model == "stable-image-ultra":
            url = f"{self.BASE_URL}/stable-image/generate/ultra"

        data = {
            "prompt": (None, prompt),
            "output_format": (None, "png"),
        }
        if "negative_prompt" in kwargs:
            data["negative_prompt"] = (None, kwargs["negative_prompt"])

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url, headers=self._headers(), files=data, timeout=120
            )
            resp.raise_for_status()
            return resp.content, prompt

    async def image_to_image(self, prompt: str, image_bytes: bytes,
                             model: str = "stable-image-core",
                             **kwargs) -> tuple[bytes, str]:
        url = f"{self.BASE_URL}/stable-image/edit/search-and-recolor"
        # Use core for image-to-image via search-and-recolor or control
        # For general img2img, use the core endpoint with an image parameter
        data = {"prompt": prompt, "output_format": "png"}
        if "strength" in kwargs:
            data["strength"] = str(kwargs["strength"])

        files = {"image": ("input.png", image_bytes, "image/png")}

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url, headers=self._headers(), data=data, files=files, timeout=120
            )
            resp.raise_for_status()
            return resp.content, prompt
