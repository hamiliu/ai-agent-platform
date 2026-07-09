from app.providers.base import ImageProvider, ModelInfo


class ImageProviderRegistry:
    _providers: dict[str, ImageProvider] = {}

    @classmethod
    def register(cls, provider: ImageProvider) -> None:
        cls._providers[provider.provider_name] = provider

    @classmethod
    def get(cls, name: str) -> ImageProvider:
        provider = cls._providers.get(name)
        if not provider:
            raise ValueError(f"Unknown image provider: {name}. "
                             f"Available: {list(cls._providers.keys())}")
        return provider

    @classmethod
    def list_all(cls) -> dict[str, list[ModelInfo]]:
        return {name: p.get_available_models()
                for name, p in cls._providers.items()}

    @classmethod
    def is_registered(cls, name: str) -> bool:
        return name in cls._providers
