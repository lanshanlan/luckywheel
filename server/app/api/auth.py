import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config import settings
from app.utils.database import get_db, User
from app.utils.security import create_access_token
from app.schemas.schemas import LoginRequest, LoginResponse, UserResponse

router = APIRouter()


async def get_wechat_openid(code: str) -> str:
    """
    通过微信code获取openid
    文档: https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
    """
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if "errcode" in data and data["errcode"] != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"微信登录失败: {data.get('errmsg', '未知错误')}"
        )

    return data.get("openid")


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录
    前端传入code，后端换取openid并返回token
    """
    # 获取openid
    openid = await get_wechat_openid(request.code)

    # 查找或创建用户
    user = db.query(User).filter(User.openid == openid).first()

    if not user:
        user = User(openid=openid)
        db.add(user)
        db.commit()
        db.refresh(user)

    # 生成token
    token = create_access_token(data={"sub": str(user.id)})

    return LoginResponse(
        token=token,
        user=UserResponse.model_validate(user)
    )