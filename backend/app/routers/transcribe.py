from io import BytesIO
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.audio_convert import ensure_supported_or_convert_to_mp3, is_supported_audio
from app.services.transcription import transcribe_audio_file
from app.services.formatting import format_transcript


router = APIRouter(prefix="/transcribe", tags=["transcribe"])


@router.post("")
async def transcribe(
    file: UploadFile = File(...),
    format_output: bool = True,
    language: Optional[str] = None,
) -> dict:
    try:
        # Save upload to a temp file first
        data = await file.read()
        tmp_dir = Path.cwd() / "_tmp_uploads"
        tmp_dir.mkdir(exist_ok=True)
        src_path = tmp_dir / file.filename
        src_path.write_bytes(data)

        # Ensure compatible format
        prepared_path = ensure_supported_or_convert_to_mp3(src_path)

        # Transcribe
        text = transcribe_audio_file(prepared_path, language=language, temperature=0.0)

        # Optional formatting
        formatted = None
        if format_output and text:
            formatted = format_transcript(text)

        return {"text": text, "formattedText": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")


