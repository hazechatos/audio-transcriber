import logging
from pathlib import Path
from typing import Optional

from app.clients.openai_client import get_openai_client
from app.clients.mistral_client import get_mistral_client
from app.config import settings

logger = logging.getLogger(__name__)

PROVIDER = settings.provider

def transcribe_audio_file_openai(file_path: Path, *, language: Optional[str] = None, temperature: float = 0.0) -> str:
    logger.info(f"Starting OpenAI transcription: {file_path} (language={language}, temperature={temperature})")
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
    text = getattr(result, "text", "")
    logger.info(f"OpenAI transcription completed. Text length: {len(text)} characters")
    return text

def transcribe_audio_file_mistral(file_path: Path, *, language: Optional[str] = None, temperature: float = 0.0) -> str:
    logger.info(f"Starting Mistral transcription: {file_path} (language={language}, temperature={temperature})")
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
    text = getattr(result, "text", "")
    logger.info(f"Mistral transcription completed. Text length: {len(text)} characters")
    return text

def transcribe_audio_file(file_path: Path, *, language: Optional[str], temperature: float):
    logger.debug(f"Transcribing with provider: {PROVIDER}")
    if PROVIDER == "mistral":
        return transcribe_audio_file_mistral(file_path, language=language, temperature=temperature)
    elif PROVIDER == "openai":
        return transcribe_audio_file_openai(file_path, language=language, temperature=temperature)
    else:
        logger.error(f"Unknown provider: {PROVIDER}")
        raise ValueError(f"Unknown provider: {PROVIDER}")

