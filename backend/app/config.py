from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Chat providers
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # Image providers
    OPENAI_IMAGE_API_KEY: str = ""
    STABILITY_API_KEY: str = ""
    ALIBABA_API_KEY: str = ""

    # Voice providers
    ELEVENLABS_API_KEY: str = ""

    # Supabase (production)
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "uploads"

    # App settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    MAX_UPLOAD_SIZE_MB: int = 20

    # CORS: JSON array of allowed origins
    CORS_ORIGINS: str = '["http://localhost:5173", "http://127.0.0.1:5173"]'

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
