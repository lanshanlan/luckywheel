from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.utils.database import get_db, Activity, Prize
from app.schemas.schemas import ActivityResponse, ActivityDetailResponse, PrizeResponse

router = APIRouter()


@router.get("", response_model=List[ActivityResponse])
async def get_activities(
    status: int = None,
    db: Session = Depends(get_db)
):
    """
    获取活动列表
    可按状态筛选：0-未开始，1-进行中，2-已结束
    """
    query = db.query(Activity)

    if status is not None:
        query = query.filter(Activity.status == status)

    activities = query.order_by(Activity.created_at.desc()).all()
    return activities


@router.get("/{activity_id}", response_model=ActivityDetailResponse)
async def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """
    获取活动详情，包含奖品列表
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )

    # 获取奖品列表，按sort_order排序
    prizes = db.query(Prize).filter(
        Prize.activity_id == activity_id
    ).order_by(Prize.sort_order).all()

    return ActivityDetailResponse(
        id=activity.id,
        title=activity.title,
        description=activity.description,
        status=activity.status,
        start_time=activity.start_time,
        end_time=activity.end_time,
        created_at=activity.created_at,
        prizes=[PrizeResponse.model_validate(p) for p in prizes]
    )