"""
用户信息接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.database import get_db, User
from app.utils.security import get_current_user
from app.schemas.schemas import UserUpdate, UserProfileResponse

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息
    """
    return current_user


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户信息（昵称）
    """
    # 验证昵称
    if update_data.nickname is not None:
        nickname = update_data.nickname.strip()
        if not nickname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="昵称不能为空"
            )
        if len(nickname) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="昵称不能超过20个字符"
            )
        current_user.nickname = nickname

    db.commit()
    db.refresh(current_user)
    return current_user