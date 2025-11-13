from pathlib import Path
from typing import Optional

from app.clients.openai_client import get_openai_client
from app.clients.mistral_client import get_mistral_client

PROVIDER = "mistral" # set to "mistral" or "openai" depending on your API subscription

def transcribe_audio_file_openai(file_path: Path, *, language: Optional[str] = None, temperature: float = 0.0) -> str:
    client = get_openai_client()
    model = "whisper-1"
    with open(file_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model=model,
            file=f,
            language=language,
            temperature=temperature,
        )
    # SDK returns an object with .text
    return getattr(result, "text", "")

def transcribe_audio_file_mistral(file_path: Path, *, language: Optional[str] = None, temperature: float = 0.0) -> str:
    client = get_mistral_client()
    model = "voxtral-mini-latest"
    with open(file_path, "rb") as f:
        result = client.audio.transcriptions.complete(
            model=model,
            file={
                "content": f,
                "file_name": "audio.mp3",
            },
            language=language,
            temperature=temperature,

        )
    return getattr(result, "text", "")

def transcribe_audio_file(file_path: Path, *, language: Optional[str], temperature: float):
    if PROVIDER == "mistral":
        return transcribe_audio_file_mistral(file_path, language=language, temperature=temperature)
    elif PROVIDER == "openai":
        return transcribe_audio_file_openai(file_path, language=language, temperature=temperature)