import random
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.utils.database import get_db, User, Activity, Prize, LotteryRecord, GuaranteeRecord
from app.utils.security import get_current_user
from app.schemas.schemas import (
    DrawRequest, DrawResponse, LotteryRecordResponse, CheckResponse, PrizeResponse, RoundInfo,
    GuaranteeRecordResponse
)
from app.services.lottery_service import draw_prize, update_guarantee_counts, get_or_create_guarantee_record

router = APIRouter()


def get_current_round(activity: Activity) -> int:
    """计算当前轮次"""
    if not activity.start_time:
        return 1
    today = datetime.now().date()
    start_date = activity.start_time.date()
    days_passed = (today - start_date).days
    interval = activity.draw_interval_days or 1
    return days_passed // interval + 1


def get_next_round_date(activity: Activity) -> str:
    """计算下轮抽奖日期"""
    if not activity.start_time:
        return None
    today = datetime.now().date()
    start_date = activity.start_time.date()
    interval = activity.draw_interval_days or 1
    current_round = get_current_round(activity)
    next_round_start = start_date + timedelta(days=current_round * interval)
    return next_round_start.strftime('%Y-%m-%d')


@router.post("/draw", response_model=DrawResponse)
async def lottery_draw(
    request: DrawRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    执行抽奖（支持心愿机制）
    每人每个活动每轮只能抽一次
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

    # 计算当前轮次
    current_round = get_current_round(activity)

    # 检查当前轮次是否已抽奖
    existing_record = db.query(LotteryRecord).filter(
        LotteryRecord.user_id == current_user.id,
        LotteryRecord.activity_id == request.activity_id,
        LotteryRecord.round_number == current_round
    ).first()

    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您的抽奖机会已用完，请等待下一轮抽奖"
        )

    # 获取所有奖品列表（包括库存为0的神秘大奖，心愿功能可能需要）
    prizes = db.query(Prize).filter(
        Prize.activity_id == request.activity_id
    ).order_by(Prize.sort_order).all()

    # 执行抽奖（传入心愿相关参数）
    won_prize, is_won, is_guarantee_triggered, progress_info = draw_prize(
        prizes, db, current_user.id, request.activity_id
    )

    # 如果心愿触发但奖品库存为0，心愿失效，改为正常抽奖（排除无库存奖品）
    if is_guarantee_triggered and won_prize and won_prize.stock <= 0:
        # 心愿失效，重新正常抽奖
        prizes_with_stock = [p for p in prizes if p.stock > 0]
        won_prize, is_won, is_guarantee_triggered, progress_info = draw_prize(
            prizes_with_stock, db, current_user.id, request.activity_id
        )

    # 创建抽奖记录
    record = LotteryRecord(
        user_id=current_user.id,
        activity_id=request.activity_id,
        prize_id=won_prize.id if won_prize else None,
        is_won=1 if is_won else 0,
        round_number=current_round
    )

    # 扣减库存（谢谢惠顾也要扣减）
    if won_prize:
        won_prize.stock -= 1

    db.add(record)

    # 更新心愿计数
    mystery_prizes = [p for p in prizes if p.prize_type == 1]
    if mystery_prizes:
        update_guarantee_counts(
            db, current_user.id, request.activity_id,
            mystery_prizes, won_prize, is_guarantee_triggered
        )

    db.commit()

    message = "恭喜中奖！"
    if is_guarantee_triggered and is_won:
        message = "恭喜心愿达成，获得神秘大奖！"
    elif is_won:
        message = "恭喜中奖！"
    else:
        message = "很遗憾，未中奖"

    return DrawResponse(
        success=True,
        is_won=is_won,
        prize=PrizeResponse.model_validate(won_prize) if won_prize else None,
        message=message,
        is_guarantee_triggered=is_guarantee_triggered
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
            round_number=record.round_number or 1,
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
    检查是否已参与过某活动（当前轮次）
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )

    current_round = get_current_round(activity)
    next_round_date = get_next_round_date(activity)

    record = db.query(LotteryRecord).filter(
        LotteryRecord.user_id == current_user.id,
        LotteryRecord.activity_id == activity_id,
        LotteryRecord.round_number == current_round
    ).first()

    if not record:
        return CheckResponse(
            has_drawn=False,
            record=None,
            round_info=RoundInfo(
                current_round=current_round,
                next_round_date=next_round_date
            )
        )

    prize = db.query(Prize).filter(Prize.id == record.prize_id).first() if record.prize_id else None

    return CheckResponse(
        has_drawn=True,
        record=LotteryRecordResponse(
            id=record.id,
            activity_id=record.activity_id,
            activity_title=activity.title,
            prize_id=record.prize_id,
            prize_name=prize.name if prize else None,
            is_won=bool(record.is_won),
            round_number=record.round_number or 1,
            created_at=record.created_at
        ),
        round_info=RoundInfo(
            current_round=current_round,
            next_round_date=next_round_date
        )
    )


@router.get("/guarantee/{activity_id}", response_model=List[GuaranteeRecordResponse])
async def get_guarantee_progress(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户在某活动中的心愿进度
    """
    # 获取该活动的所有神秘大奖
    mystery_prizes = db.query(Prize).filter(
        Prize.activity_id == activity_id,
        Prize.prize_type == 1,
        Prize.guarantee_count > 0
    ).all()

    result = []
    for prize in mystery_prizes:
        record = get_or_create_guarantee_record(
            db, current_user.id, activity_id, prize.id
        )
        result.append(GuaranteeRecordResponse(
            prize_id=prize.id,
            prize_name=prize.name,
            guarantee_count=prize.guarantee_count,
            current_count=record.current_count,
            remaining_count=max(0, prize.guarantee_count - record.current_count - 1)
        ))

    return result