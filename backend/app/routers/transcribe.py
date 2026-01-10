import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.preprocessor import preprocess
from app.services.transcriber import transcribe_audio_file
from app.services.formatter import format_transcript

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/transcribe", tags=["transcribe"])


@router.post("")
async def transcribe(
    files: list[UploadFile] = File(...),
    format_output: bool = True,
    language: Optional[str] = None,
) -> dict:
    filenames = [f.filename for f in files]
    logger.info(
        f"Received transcription request: filenames={filenames}, format_output={format_output}, language={language}"
    )
    try:
        tmp_dir = Path.cwd() / "_tmp_uploads"
        tmp_dir.mkdir(exist_ok=True)

        src_paths = []
        for file in files:
            data = await file.read()
            src_path = tmp_dir / file.filename
            src_path.write_bytes(data)
            src_paths.append(src_path)

        # Preprocess (concatenate if multiple and ensure compatible)
        prepared_path = preprocess(src_paths)

        # Transcribe 
        text = transcribe_audio_file(prepared_path, language=language, temperature=0.0)

        # Optional formatting 
        formatted = None
        if format_output and text:
            formatted = format_transcript(text)

        logger.info(f"Transcription request completed successfully for: {filenames}")
        return {"text": text, "formattedText": formatted}
    except Exception as e:
        logger.error(f"Transcription request failed for {filenames}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")


