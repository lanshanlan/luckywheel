"""
管理接口 - 活动和奖品管理
"""
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.utils.database import get_db, User, Activity, Prize, LotteryRecord
from app.utils.security import get_current_user, get_current_admin
from app.schemas.schemas import (
    ActivityCreate, ActivityUpdate, ActivityResponse,
    PrizeCreate, PrizeUpdate, PrizeResponse,
    LotteryRecordResponse
)

router = APIRouter()

# "谢谢惠顾"奖品的默认名称
THANKS_PRIZE_NAME = "谢谢惠顾"


def get_thanks_prize(db: Session, activity_id: int) -> Prize:
    """获取活动的谢谢惠顾奖品"""
    return db.query(Prize).filter(
        Prize.activity_id == activity_id,
        Prize.name == THANKS_PRIZE_NAME
    ).first()


def update_thanks_prize_probability(db: Session, activity_id: int):
    """更新谢谢惠顾的概率，使其等于1减去其他所有奖品的概率之和"""
    thanks_prize = get_thanks_prize(db, activity_id)
    if not thanks_prize:
        return

    # 计算其他奖品的概率之和
    other_prizes = db.query(Prize).filter(
        Prize.activity_id == activity_id,
        Prize.id != thanks_prize.id
    ).all()

    total_prob = sum(p.probability for p in other_prizes)
    thanks_prize.probability = Decimal('1') - total_prob

    # 确保概率不为负
    if thanks_prize.probability < 0:
        thanks_prize.probability = Decimal('0')

    db.commit()


# ============ 管理员验证 ============

@router.get("/check")
async def check_admin(current_user: User = Depends(get_current_admin)):
    """检查是否为管理员"""
    return {"is_admin": True, "user_id": current_user.id, "nickname": current_user.nickname}


# ============ 活动管理 ============

@router.post("/activities", response_model=ActivityResponse)
async def create_activity(
    activity_data: ActivityCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建活动，自动添加"谢谢惠顾"奖品"""
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

    # 自动添加"谢谢惠顾"奖品，概率为1，库存100000
    thanks_prize = Prize(
        activity_id=activity.id,
        name=THANKS_PRIZE_NAME,
        probability=Decimal('1'),
        stock=100000,
        sort_order=999  # 放在最后
    )
    db.add(thanks_prize)
    db.commit()

    return activity


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    current_user: User = Depends(get_current_admin),
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
    current_user: User = Depends(get_current_admin),
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
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """添加奖品，自动调整谢谢惠顾的概率"""
    # 检查活动是否存在
    activity = db.query(Activity).filter(Activity.id == prize_data.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    # 不允许手动添加"谢谢惠顾"奖品
    if prize_data.name == THANKS_PRIZE_NAME:
        raise HTTPException(status_code=400, detail="系统会自动添加谢谢惠顾奖品，无需手动添加")

    # 计算现有奖品（除谢谢惠顾外）的概率之和
    thanks_prize = get_thanks_prize(db, prize_data.activity_id)
    existing_prizes = db.query(Prize).filter(
        Prize.activity_id == prize_data.activity_id,
        Prize.id != thanks_prize.id if thanks_prize else None
    ).all()
    existing_total_prob = sum(p.probability for p in existing_prizes)

    # 检查添加新奖品后总概率是否超过1
    if existing_total_prob + prize_data.probability > Decimal('1'):
        raise HTTPException(
            status_code=400,
            detail=f"奖品总概率不可超过100%，当前已使用{float(existing_total_prob)*100:.2f}%"
        )

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

    # 更新谢谢惠顾的概率
    update_thanks_prize_probability(db, prize_data.activity_id)

    return prize


@router.put("/prizes/{prize_id}", response_model=PrizeResponse)
async def update_prize(
    prize_id: int,
    prize_data: PrizeUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """修改奖品，自动调整谢谢惠顾的概率"""
    prize = db.query(Prize).filter(Prize.id == prize_id).first()
    if not prize:
        raise HTTPException(status_code=404, detail="奖品不存在")

    # 不允许修改谢谢惠顾的名称
    if prize.name == THANKS_PRIZE_NAME and prize_data.name and prize_data.name != THANKS_PRIZE_NAME:
        raise HTTPException(status_code=400, detail="不允许修改谢谢惠顾奖品的名称")

    # 如果修改了概率，需要检查总概率是否超过1
    if prize_data.probability is not None and prize.name != THANKS_PRIZE_NAME:
        thanks_prize = get_thanks_prize(db, prize.activity_id)
        other_prizes = db.query(Prize).filter(
            Prize.activity_id == prize.activity_id,
            Prize.id != prize_id,
            Prize.id != thanks_prize.id if thanks_prize else None
        ).all()
        other_total_prob = sum(p.probability for p in other_prizes)

        if other_total_prob + prize_data.probability > Decimal('1'):
            raise HTTPException(
                status_code=400,
                detail=f"奖品总概率不可超过100%，当前其他奖品已使用{float(other_total_prob)*100:.2f}%"
            )

    update_data = prize_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prize, key, value)

    db.commit()
    db.refresh(prize)

    # 如果修改了概率，更新谢谢惠顾的概率
    if 'probability' in update_data:
        update_thanks_prize_probability(db, prize.activity_id)

    return prize


@router.delete("/prizes/{prize_id}")
async def delete_prize(
    prize_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除奖品，自动调整谢谢惠顾的概率"""
    prize = db.query(Prize).filter(Prize.id == prize_id).first()
    if not prize:
        raise HTTPException(status_code=404, detail="奖品不存在")

    # 不允许删除谢谢惠顾奖品
    if prize.name == THANKS_PRIZE_NAME:
        raise HTTPException(status_code=400, detail="不允许删除谢谢惠顾奖品")

    activity_id = prize.activity_id
    db.delete(prize)
    db.commit()

    # 更新谢谢惠顾的概率
    update_thanks_prize_probability(db, activity_id)

    return {"success": True, "message": "奖品已删除"}


# ============ 抽奖记录管理 ============

@router.get("/records", response_model=List[LotteryRecordResponse])
async def get_all_records(
    activity_id: int = None,
    current_user: User = Depends(get_current_admin),
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