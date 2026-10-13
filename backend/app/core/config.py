from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "REHAB-TWIN"
    api_prefix: str = "/api"
    db_url: str = "sqlite:///./rehab_twin.db"
    demo_mode: bool = True
    model_dir: str = "./backend/artifacts"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_upload_size_mb: int = 12
    allowed_image_types: tuple[str, ...] = ("image/png", "image/jpeg")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        extra="ignore",
        protected_namespaces=(),
    )


settings = Settings()
