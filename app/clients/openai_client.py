from openai import OpenAI
from app.config import settings


def get_openai_client() -> OpenAI:
    # The SDK reads OPENAI_API_KEY from env automatically.
    # This function provides a single import point for services.
    if not settings.openai_api_key:
        # Still return a client; auth error will be raised on first call.
        pass
    return OpenAI()


