import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.voice.registry import VoiceProviderRegistry
from app.utils.file_storage import get_file_bytes, upload_bytes


class VoiceService:
    @staticmethod
    async def clone_and_speak(
        provider_name: str,
        text: str,
        sample_file_ids: list[str],
        model: str = "",
        db: AsyncSession | None = None,
        **kwargs,
    ) -> dict:
        provider = VoiceProviderRegistry.get(provider_name)
        model = model or provider.get_available_models()[0].id

        # Read audio samples from Supabase Storage
        audio_samples: list[bytes] = []
        for file_id in sample_file_ids:
            data = await get_file_bytes(file_id)
            if not data:
                raise FileNotFoundError(f"Audio file not found: {file_id}")
            audio_samples.append(data)

        if not audio_samples:
            raise ValueError("At least one audio sample is required for voice cloning.")

        audio_bytes = await provider.clone_and_speak(
            audio_samples, text, model=model, **kwargs
        )

        # Upload audio to Supabase Storage
        filename = f"{uuid.uuid4().hex}.mp3"
        url = await upload_bytes(audio_bytes, filename)

        if db:
            from app.models import GenerationRecord
            record = GenerationRecord(
                gen_type="voice-clone",
                provider=provider_name,
                model=model,
                prompt=text,
                output_file_path=url,
            )
            db.add(record)
            await db.commit()

        return {"audio_url": url}
