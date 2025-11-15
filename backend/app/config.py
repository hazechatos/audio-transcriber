import os
from typing import List

from dotenv import load_dotenv


load_dotenv()


class Settings:
    @property
    def openai_api_key(self) -> str:
        return os.environ.get("OPENAI_API_KEY", "")

    @property
    def mistral_api_key(self) -> str:
        return os.environ.get("MISTRAL_API_KEY", "")

    @property
    def allowed_origins(self) -> List[str]:
        raw = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")
        return [s.strip() for s in raw.split(",") if s.strip()]

    @property
    def log_level(self) -> str:
        return os.environ.get("LOG_LEVEL", "INFO")

    @property
    def provider(self) -> str:
        return os.environ.get("PROVIDER", "mistral")


settings = Settings()


