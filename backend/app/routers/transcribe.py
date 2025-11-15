import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.audio_converter import ensure_supported_or_convert_to_mp3
from app.services.transcriber import transcribe_audio_file
from app.services.formatter import format_transcript

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/transcribe", tags=["transcribe"])


@router.post("")
async def transcribe(
    file: UploadFile = File(...),
    format_output: bool = True,
    language: Optional[str] = None,
) -> dict:
    logger.info(
        f"Received transcription request: filename={file.filename}, "
        f"content_type={file.content_type}, format_output={format_output}, language={language}"
    )
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

        logger.info(f"Transcription request completed successfully for: {file.filename}")
        return {"text": text, "formattedText": formatted}
    except Exception as e:
        logger.error(f"Transcription request failed for {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")


