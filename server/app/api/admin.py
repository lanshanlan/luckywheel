"""
管理接口 - 活动和奖品管理
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.utils.database import get_db, User, Activity, Prize, LotteryRecord
from app.utils.security import get_current_user
from app.schemas.schemas import (
    ActivityCreate, ActivityUpdate, ActivityResponse,
    PrizeCreate, PrizeUpdate, PrizeResponse,
    LotteryRecordResponse
)

router = APIRouter()


# ============ 活动管理 ============

@router.post("/activities", response_model=ActivityResponse)
async def create_activity(
    activity_data: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建活动"""
    activity = Activity(
        title=activity_data.title,
        description=activity_data.description,
        status=activity_data.status,
        start_time=activity_data.start_time,
        end_time=activity_data.end_time
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改活动"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    update_data = activity_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(activity, key, value)

    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/activities/{activity_id}")
async def delete_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除活动"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    db.delete(activity)
    db.commit()
    return {"success": True, "message": "活动已删除"}


# ============ 奖品管理 ============

@router.post("/prizes", response_model=PrizeResponse)
async def create_prize(
    prize_data: PrizeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加奖品"""
    # 检查活动是否存在
    activity = db.query(Activity).filter(Activity.id == prize_data.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    prize = Prize(
        activity_id=prize_data.activity_id,
        name=prize_data.name,
        image_url=prize_data.image_url,
        probability=prize_data.probability,
        stock=prize_data.stock,
        sort_order=prize_data.sort_order
    )
    db.add(prize)
    db.commit()
    db.refresh(prize)
    return prize


@router.put("/prizes/{prize_id}", response_model=PrizeResponse)
async def update_prize(
    prize_id: int,
    prize_data: PrizeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改奖品"""
    prize = db.query(Prize).filter(Prize.id == prize_id).first()
    if not prize:
        raise HTTPException(status_code=404, detail="奖品不存在")

    update_data = prize_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prize, key, value)

    db.commit()
    db.refresh(prize)
    return prize


@router.delete("/prizes/{prize_id}")
async def delete_prize(
    prize_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除奖品"""
    prize = db.query(Prize).filter(Prize.id == prize_id).first()
    if not prize:
        raise HTTPException(status_code=404, detail="奖品不存在")

    db.delete(prize)
    db.commit()
    return {"success": True, "message": "奖品已删除"}


# ============ 抽奖记录管理 ============

@router.get("/records", response_model=List[LotteryRecordResponse])
async def get_all_records(
    activity_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询所有抽奖记录（可按活动筛选）"""
    query = db.query(LotteryRecord)

    if activity_id:
        query = query.filter(LotteryRecord.activity_id == activity_id)

    records = query.order_by(LotteryRecord.created_at.desc()).all()

    result = []
    for record in records:
        user = db.query(User).filter(User.id == record.user_id).first()
        activity = db.query(Activity).filter(Activity.id == record.activity_id).first()
        prize = db.query(Prize).filter(Prize.id == record.prize_id).first() if record.prize_id else None

        result.append(LotteryRecordResponse(
            id=record.id,
            activity_id=record.activity_id,
            activity_title=activity.title if activity else None,
            prize_id=record.prize_id,
            prize_name=prize.name if prize else None,
            is_won=bool(record.is_won),
            created_at=record.created_at
        ))

    return result