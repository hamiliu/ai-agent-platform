import uuid
import httpx

from app.providers.base import VoiceProvider, ModelInfo


class ElevenLabsVoiceProvider(VoiceProvider):
    provider_name = "elevenlabs"
    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _headers(self) -> dict:
        return {"xi-api-key": self.api_key}

    def get_available_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(id="eleven_multilingual_v2", name="Eleven Multilingual v2",
                      provider="elevenlabs",
                      capabilities=["tts", "voice-cloning"]),
            ModelInfo(id="eleven_turbo_v2_5", name="Eleven Turbo v2.5",
                      provider="elevenlabs",
                      capabilities=["tts"]),
        ]

    async def clone_and_speak(self, audio_samples: list[bytes], text: str,
                              **kwargs) -> bytes:
        voice_name = f"temp_voice_{uuid.uuid4().hex[:8]}"

        # Step 1: Clone voice
        async with httpx.AsyncClient() as client:
            files = [("files", (f"sample_{i}.wav", sample, "audio/wav"))
                     for i, sample in enumerate(audio_samples)]
            files.append(("name", (None, voice_name)))

            resp = await client.post(
                f"{self.BASE_URL}/voices/add",
                headers=self._headers(),
                files=files,
                timeout=120,
            )
            resp.raise_for_status()
            voice_id = resp.json()["voice_id"]

        # Step 2: Generate speech with cloned voice
        model_id = kwargs.get("model", "eleven_multilingual_v2")
        voice_settings = {
            "stability": kwargs.get("stability", 0.5),
            "similarity_boost": kwargs.get("similarity_boost", 0.8),
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/text-to-speech/{voice_id}",
                headers={**self._headers(), "Content-Type": "application/json"},
                json={
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": voice_settings,
                },
                timeout=120,
            )
            resp.raise_for_status()

            # Delete the cloned voice to avoid clutter
            try:
                await client.delete(
                    f"{self.BASE_URL}/voices/{voice_id}",
                    headers=self._headers(),
                )
            except Exception:
                pass  # Non-critical cleanup

            return resp.content

    async def text_to_speech(self, text: str, voice_id: str = "",
                             **kwargs) -> bytes:
        model_id = kwargs.get("model", "eleven_multilingual_v2")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/text-to-speech/{voice_id}",
                headers={**self._headers(), "Content-Type": "application/json"},
                json={
                    "text": text,
                    "model_id": model_id,
                },
                timeout=120,
            )
            resp.raise_for_status()
            return resp.content
