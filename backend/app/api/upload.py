import uuid
from pathlib import Path
from typing import Dict
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import get_current_user
from app.config import settings
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED = {"image/jpeg", "image/png", "image/gif", "image/webp"}
EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}
MAX_BYTES = 5 * 1024 * 1024


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(
    _: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
) -> Dict[str, str]:
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image type")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")
    ext = EXT[file.content_type]
    name = f"{uuid.uuid4().hex}{ext}"
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / name
    path.write_bytes(data)
    return {"url": f"/static/uploads/{name}"}
