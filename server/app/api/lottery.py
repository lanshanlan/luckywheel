import random
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.utils.database import get_db, User, Activity, Prize, LotteryRecord
from app.utils.security import get_current_user
from app.schemas.schemas import (
    DrawRequest, DrawResponse, LotteryRecordResponse, CheckResponse, PrizeResponse
)
from app.services.lottery_service import draw_prize

router = APIRouter()


@router.post("/draw", response_model=DrawResponse)
async def lottery_draw(
    request: DrawRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    执行抽奖
    每人每个活动只能抽一次
    """
    # 检查活动是否存在且进行中
    activity = db.query(Activity).filter(Activity.id == request.activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )

    if activity.status != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="活动未开始或已结束"
        )

    # 检查是否已参与过
    existing_record = db.query(LotteryRecord).filter(
        LotteryRecord.user_id == current_user.id,
        LotteryRecord.activity_id == request.activity_id
    ).first()

    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已参与过本次活动"
        )

    # 获取奖品列表
    prizes = db.query(Prize).filter(
        Prize.activity_id == request.activity_id,
        Prize.stock > 0
    ).all()

    # 执行抽奖
    won_prize = draw_prize(prizes)

    # 创建抽奖记录
    record = LotteryRecord(
        user_id=current_user.id,
        activity_id=request.activity_id,
        prize_id=won_prize.id if won_prize else None,
        is_won=1 if won_prize else 0
    )

    # 扣减库存
    if won_prize:
        won_prize.stock -= 1

    db.add(record)
    db.commit()

    return DrawResponse(
        success=True,
        is_won=bool(won_prize),
        prize=PrizeResponse.model_validate(won_prize) if won_prize else None,
        message="恭喜中奖！" if won_prize else "很遗憾，未中奖"
    )


@router.get("/records", response_model=List[LotteryRecordResponse])
async def get_my_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取我的抽奖记录
    """
    records = db.query(LotteryRecord).filter(
        LotteryRecord.user_id == current_user.id
    ).order_by(LotteryRecord.created_at.desc()).all()

    result = []
    for record in records:
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


@router.get("/check/{activity_id}", response_model=CheckResponse)
async def check_drawn(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    检查是否已参与过某活动
    """
    record = db.query(LotteryRecord).filter(
        LotteryRecord.user_id == current_user.id,
        LotteryRecord.activity_id == activity_id
    ).first()

    if not record:
        return CheckResponse(has_drawn=False, record=None)

    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    prize = db.query(Prize).filter(Prize.id == record.prize_id).first() if record.prize_id else None

    return CheckResponse(
        has_drawn=True,
        record=LotteryRecordResponse(
            id=record.id,
            activity_id=record.activity_id,
            activity_title=activity.title if activity else None,
            prize_id=record.prize_id,
            prize_name=prize.name if prize else None,
            is_won=bool(record.is_won),
            created_at=record.created_at
        )
    )