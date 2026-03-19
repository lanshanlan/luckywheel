from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============ 用户相关 ============
class UserBase(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    openid: str


class UserResponse(UserBase):
    id: int
    openid: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 登录相关 ============
class LoginRequest(BaseModel):
    code: str  # 微信登录code


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


# ============ 活动相关 ============
class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: int = 1
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    draw_interval_days: int = 1


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    draw_interval_days: Optional[int] = None


class ActivityResponse(ActivityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityDetailResponse(ActivityResponse):
    prizes: List["PrizeResponse"] = []


# ============ 奖品相关 ============
class PrizeBase(BaseModel):
    name: str
    image_url: Optional[str] = None
    probability: Decimal
    stock: int = 0
    sort_order: int = 0


class PrizeCreate(PrizeBase):
    activity_id: int


class PrizeUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = None
    probability: Optional[Decimal] = None
    stock: Optional[int] = None
    sort_order: Optional[int] = None


class PrizeResponse(PrizeBase):
    id: int
    activity_id: int

    class Config:
        from_attributes = True


# ============ 抽奖相关 ============
class DrawRequest(BaseModel):
    activity_id: int


class DrawResponse(BaseModel):
    success: bool
    is_won: bool
    prize: Optional[PrizeResponse] = None
    message: str


class LotteryRecordResponse(BaseModel):
    id: int
    activity_id: int
    activity_title: Optional[str] = None
    prize_id: Optional[int] = None
    prize_name: Optional[str] = None
    is_won: bool
    round_number: int = 1
    created_at: datetime

    class Config:
        from_attributes = True


class RoundInfo(BaseModel):
    current_round: int  # 当前轮次
    next_round_date: Optional[str] = None  # 下轮抽奖日期


class CheckResponse(BaseModel):
    has_drawn: bool
    record: Optional[LotteryRecordResponse] = None
    round_info: Optional[RoundInfo] = None


# 更新forward reference
ActivityDetailResponse.model_rebuild()