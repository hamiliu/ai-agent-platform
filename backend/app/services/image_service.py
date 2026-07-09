import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.image.registry import ImageProviderRegistry
from app.utils.file_storage import get_file_bytes, upload_bytes


class ImageService:
    @staticmethod
    async def generate_text_to_image(
        provider_name: str,
        prompt: str,
        model: str = "",
        db: AsyncSession | None = None,
        **kwargs,
    ) -> dict:
        provider = ImageProviderRegistry.get(provider_name)
        model = model or provider.get_available_models()[0].id

        image_bytes, revised_prompt = await provider.text_to_image(
            prompt, model=model, **kwargs
        )

        # Upload to Supabase Storage
        filename = f"{uuid.uuid4().hex}.png"
        url = await upload_bytes(image_bytes, filename)

        # Save record to DB if available
        if db:
            from app.models import GenerationRecord
            record = GenerationRecord(
                gen_type="text-to-image",
                provider=provider_name,
                model=model,
                prompt=prompt,
                output_file_path=url,
            )
            db.add(record)
            await db.commit()

        return {"url": url, "revised_prompt": revised_prompt}

    @staticmethod
    async def generate_image_to_image(
        provider_name: str,
        prompt: str,
        image_file_id: str,
        model: str = "",
        db: AsyncSession | None = None,
        **kwargs,
    ) -> dict:
        provider = ImageProviderRegistry.get(provider_name)
        model = model or provider.get_available_models()[0].id

        # Read input file from Supabase Storage
        image_bytes = await get_file_bytes(image_file_id)
        if not image_bytes:
            raise FileNotFoundError(f"File not found: {image_file_id}")

        image_bytes, revised_prompt = await provider.image_to_image(
            prompt, image_bytes, model=model, **kwargs
        )

        # Upload output to Supabase Storage
        filename = f"{uuid.uuid4().hex}.png"
        url = await upload_bytes(image_bytes, filename)

        if db:
            from app.models import GenerationRecord
            record = GenerationRecord(
                gen_type="image-to-image",
                provider=provider_name,
                model=model,
                prompt=prompt,
                output_file_path=url,
            )
            db.add(record)
            await db.commit()

        return {"url": url, "revised_prompt": revised_prompt}
