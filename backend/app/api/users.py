import uuid
from pathlib import Path
from typing import Dict
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import _user_out
from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserOut
from app.schemas.user_profile import PasswordChange, UserProfileUpdate
from app.security import hash_password, verify_password
from app.config import settings

router = APIRouter(prefix="/users", tags=["users"])

ALLOWED_AVATAR = {"image/jpeg", "image/png", "image/gif", "image/webp"}
EXT_AVATAR = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}
MAX_AVATAR = 3 * 1024 * 1024


@router.get("/me", response_model=UserOut)
async def get_profile(user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return _user_out(user)


@router.patch("/me", response_model=UserOut)
async def patch_profile(
    body: UserProfileUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserOut:
    data = body.model_dump(exclude_unset=True)
    if "first_name" in data:
        user.first_name = body.first_name.strip() if body.first_name else None
    if "last_name" in data:
        user.last_name = body.last_name.strip() if body.last_name else None
    if "hourly_rate" in data and body.hourly_rate is not None:
        user.hourly_rate = body.hourly_rate
    await db.commit()
    await db.refresh(user)
    return _user_out(user)


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: PasswordChange,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    if not verify_password(body.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный текущий пароль")
    user.hashed_password = hash_password(body.new_password)
    await db.commit()


@router.post("/me/avatar", status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
) -> Dict[str, str]:
    if file.content_type not in ALLOWED_AVATAR:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неподдерживаемый формат изображения")
    data = await file.read()
    if len(data) > MAX_AVATAR:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл слишком большой")
    ext = EXT_AVATAR[file.content_type]
    name = f"{uuid.uuid4().hex}{ext}"
    av_dir = Path(settings.upload_dir) / "avatars"
    av_dir.mkdir(parents=True, exist_ok=True)
    path = av_dir / name
    path.write_bytes(data)
    if user.avatar_filename:
        old = Path(settings.upload_dir) / "avatars" / user.avatar_filename
        if old.is_file():
            try:
                old.unlink()
            except OSError:
                pass
    user.avatar_filename = name
    await db.commit()
    await db.refresh(user)
    return {"url": f"/static/uploads/avatars/{name}"}
