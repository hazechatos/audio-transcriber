import logging
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.exporter import export_md_to_docx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["export"])


class ExportRequest(BaseModel):
    content: str


@router.post("")
async def export(
    request: ExportRequest,
) -> FileResponse:
    logger.info(
        f"Received export request, "
        f"content_size: {len(request.content)}"
    )
    try:
        # Create a temporary file for the DOCX output
        tmp_dir = Path(tempfile.gettempdir())
        tmp_dir.mkdir(exist_ok=True)
        output_path = tmp_dir / f"export_{uuid.uuid4().hex}.docx"
        
        # Export markdown to DOCX
        export_md_to_docx(request.content, str(output_path))
        
        # Return the file
        return FileResponse(
            path=str(output_path),
            filename="transcript.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        logger.error(f"Export request failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")
