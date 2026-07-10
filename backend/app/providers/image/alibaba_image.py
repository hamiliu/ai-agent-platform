import httpx
import asyncio

from app.providers.base import ImageProvider, ModelInfo

BASE_URL = "https://dashscope.aliyuncs.com/api/v1"


class AlibabaImageProvider(ImageProvider):
    provider_name = "alibaba"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }

    def get_available_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(id="wanx2.1-t2i-turbo", name="通义万相 2.1 Turbo", provider="alibaba",
                      capabilities=["text-to-image"]),
            ModelInfo(id="wanx2.1-t2i-plus", name="通义万相 2.1 Plus", provider="alibaba",
                      capabilities=["text-to-image"]),
        ]

    async def text_to_image(self, prompt: str, model: str = "wanx2.1-t2i-turbo",
                            **kwargs) -> tuple[bytes, str]:
        size = kwargs.get("size", "1024*1024")
        # DashScope uses "1024*1024" format
        size = size.replace("x", "*")

        async with httpx.AsyncClient(timeout=30) as client:
            # Step 1: Submit task
            resp = await client.post(
                f"{BASE_URL}/services/aigc/text2image/image-synthesis",
                headers=self.headers,
                json={
                    "model": model,
                    "input": {"prompt": prompt},
                    "parameters": {"size": size, "n": 1},
                },
            )
            resp.raise_for_status()
            task_data = resp.json()
            task_id = task_data["output"]["task_id"]

            # Step 2: Poll until complete
            task_status = task_data["output"]["task_status"]
            max_retries = 30  # 30 * 2s = 60s max wait
            while task_status in ("PENDING", "RUNNING") and max_retries > 0:
                await asyncio.sleep(2)
                poll_resp = await client.get(
                    f"{BASE_URL}/tasks/{task_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                poll_resp.raise_for_status()
                poll_data = poll_resp.json()
                task_status = poll_data["output"]["task_status"]
                max_retries -= 1

            if task_status != "SUCCEEDED":
                raise RuntimeError(
                    f"Image generation failed: {task_status} - "
                    f"{poll_data['output'].get('message', '')}"
                )

            # Step 3: Download the image
            image_url = poll_data["output"]["results"][0]["url"]
            revised = poll_data["output"]["results"][0].get("actual_prompt", prompt)
            img_resp = await client.get(image_url, timeout=60)
            img_resp.raise_for_status()
            return img_resp.content, revised

    async def image_to_image(self, prompt: str, image_bytes: bytes,
                             model: str = "", **kwargs) -> tuple[bytes, str]:
        raise NotImplementedError(
            "Alibaba DashScope does not support image-to-image via this provider. "
            "Use the Stability provider."
        )
