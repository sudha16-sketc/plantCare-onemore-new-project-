"""
Controlled download endpoint for generated PPTX guides.

Replaces the previous raw StaticFiles mount: only sanitized, generated
.pptx filenames inside the output directory are served, with a safe
Content-Disposition header.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.ppt_service import ppt_service

router = APIRouter(prefix="/api/v1/files", tags=["Files"])

_NO_STORE = {"Cache-Control": "private, max-age=0", "X-Content-Type-Options": "nosniff"}


@router.get("/{file_name}", summary="Download a generated care-guide presentation")
async def download_generated_file(file_name: str):
    path = ppt_service.safe_path(file_name)
    if path is None:
        # 404 for anything invalid or unknown — do not reveal filesystem detail.
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=file_name,
        headers=_NO_STORE,
    )
