from mistralai import Mistral
from app.config import settings

def get_mistral_client() -> Mistral:
    if not settings.mistral_api_key:
        pass # No error handling here
    return Mistral(api_key=settings.mistral_api_key)