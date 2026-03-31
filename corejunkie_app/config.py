from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_base_url: str = os.getenv("APP_BASE_URL", "http://localhost:8000")
    app_base_path: str = os.getenv("APP_BASE_PATH", "/app")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./corejunkie.db")


settings = Settings()
