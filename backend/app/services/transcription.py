from pathlib import Path
from typing import Optional

from app.clients.openai_client import get_openai_client


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


