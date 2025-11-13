from pathlib import Path
from typing import Optional

from app.clients.openai_client import get_openai_client
from app.clients.mistral_client import get_mistral_client

def transcribe_audio_file(file_path: Path, *, language: Optional[str] = None, temperature: float = 0.0) -> str:
    client = get_openai_client()
    with open(file_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language=language,
            temperature=temperature,
        )
    # SDK returns an object with .text
    return getattr(result, "text", "")

def transcribe_audio_file_mistral(file_path: Path, *, language: Optional[str] = None, temperature: float = 0.0) -> str:
    client = get_mistral_client()
    model = "voxtral-mini-latest"
    print("Transcribing using Mistral")
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