from app.providers.base import VoiceProvider, ModelInfo


class VoiceProviderRegistry:
    _providers: dict[str, VoiceProvider] = {}

    @classmethod
    def register(cls, provider: VoiceProvider) -> None:
        cls._providers[provider.provider_name] = provider

    @classmethod
    def get(cls, name: str) -> VoiceProvider:
        provider = cls._providers.get(name)
        if not provider:
            raise ValueError(f"Unknown voice provider: {name}. "
                             f"Available: {list(cls._providers.keys())}")
        return provider

    @classmethod
    def list_all(cls) -> dict[str, list[ModelInfo]]:
        return {name: p.get_available_models()
                for name, p in cls._providers.items()}

    @classmethod
    def is_registered(cls, name: str) -> bool:
        return name in cls._providers
