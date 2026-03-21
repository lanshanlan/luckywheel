"""
抽奖核心逻辑服务 - 支持心愿机制
"""
import random
from decimal import Decimal
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session

from app.utils.database import Prize, GuaranteeRecord


def get_or_create_guarantee_record(
    db: Session,
    user_id: int,
    activity_id: int,
    prize_id: int
) -> GuaranteeRecord:
    """
    获取或创建心愿计数记录
    """
    record = db.query(GuaranteeRecord).filter(
        GuaranteeRecord.user_id == user_id,
        GuaranteeRecord.activity_id == activity_id,
        GuaranteeRecord.prize_id == prize_id
    ).first()

    if not record:
        record = GuaranteeRecord(
            user_id=user_id,
            activity_id=activity_id,
            prize_id=prize_id,
            current_count=0
        )
        db.add(record)
        db.flush()  # 立即写入以获取ID

    return record


def check_guarantee_trigger(
    db: Session,
    user_id: int,
    activity_id: int,
    mystery_prizes: List[Prize]
) -> Tuple[Optional[Prize], List[Dict[str, Any]]]:
    """
    检查是否心愿达成

    返回:
        (触发的心愿奖品, 所有神秘大奖的心愿进度信息)

    心愿触发规则:
        1. 库存必须大于0
        2. 触发条件：current_count >= guarantee_count - 1
           即心愿5次时，计数到4就触发（抽了4次未中，第5次必中）
        3. 如果多个同时满足，优先心愿达成次数最小的（对用户最友好的）
    """
    if not mystery_prizes:
        return None, []

    guarantee_candidates = []  # 候选触发列表
    progress_info = []  # 进度信息

    for prize in mystery_prizes:
        # 跳过无心愿配置的
        if prize.guarantee_count <= 0:
            continue

        record = get_or_create_guarantee_record(db, user_id, activity_id, prize.id)

        # 计算距离心愿的次数
        remaining = prize.guarantee_count - record.current_count

        progress_info.append({
            "prize_id": prize.id,
            "prize_name": prize.name,
            "guarantee_count": prize.guarantee_count,
            "current_count": record.current_count,
            "remaining_count": max(0, remaining - 1)  # 本次抽奖后剩余
        })

        # 检查是否心愿达成：current_count >= guarantee_count - 1
        # 心愿5次：计数到4时触发（第5次必中）
        if record.current_count >= prize.guarantee_count - 1:
            # 库存必须大于0才能心愿达成
            if prize.stock > 0:
                guarantee_candidates.append((prize, prize.guarantee_count))

    # 如果有候选，优先选择心愿次数最小的（最容易被触发）
    if guarantee_candidates:
        guarantee_candidates.sort(key=lambda x: x[1])  # 按心愿次数升序
        return guarantee_candidates[0][0], progress_info

    return None, progress_info


def update_guarantee_counts(
    db: Session,
    user_id: int,
    activity_id: int,
    mystery_prizes: List[Prize],
    won_prize: Optional[Prize],
    is_guarantee_triggered: bool
) -> None:
    """
    更新心愿计数

    规则:
    1. 如果抽中了某个神秘大奖（正常抽中或心愿触发），该神秘大奖的计数重置为0
    2. 如果没有抽中神秘大奖，所有神秘大奖的计数+1
    """
    for prize in mystery_prizes:
        if prize.guarantee_count <= 0:
            continue

        record = get_or_create_guarantee_record(db, user_id, activity_id, prize.id)

        # 判断是否需要重置
        should_reset = False
        if won_prize and won_prize.id == prize.id:
            # 抽中了该神秘大奖（无论是正常抽中还是心愿触发）
            should_reset = True

        if should_reset:
            record.current_count = 0
        else:
            record.current_count += 1

    db.commit()


def draw_prize(
    prizes: List[Prize],
    db: Session = None,
    user_id: int = None,
    activity_id: int = None
) -> Tuple[Optional[Prize], bool, bool, List[Dict[str, Any]]]:
    """
    按概率随机抽取奖品（支持心愿机制）

    Args:
        prizes: 奖品列表
        db: 数据库会话（心愿机制需要）
        user_id: 用户ID（心愿机制需要）
        activity_id: 活动ID（心愿机制需要）

    Returns:
        (中奖奖品, 是否真正中奖, 是否心愿达成, 心愿进度信息)
        - 如果是普通奖品，返回 (prize, True, False, [])
        - 如果是"谢谢惠顾"奖品，返回 (prize, False, False, [])
        - 如果心愿达成，返回 (prize, True, True, progress_info)
    """
    if not prizes:
        return None, False, False, []

    # 分离神秘大奖
    mystery_prizes = [p for p in prizes if p.prize_type == 1 and p.guarantee_count > 0]

    is_guarantee_triggered = False
    progress_info = []

    # ======== 步骤1: 检查心愿触发 ========
    if db and user_id and activity_id and mystery_prizes:
        guarantee_prize, progress_info = check_guarantee_trigger(
            db, user_id, activity_id, mystery_prizes
        )

        if guarantee_prize:
            # 心愿触发，直接返回该奖品
            is_guarantee_triggered = True
            is_thanks = '谢谢' in guarantee_prize.name or '惠顾' in guarantee_prize.name
            return guarantee_prize, not is_thanks, True, progress_info

    # ======== 步骤2: 正常随机抽奖 ========
    # 生成 0-1 的随机数
    rand = random.random()

    # 累计概率
    cumulative = Decimal('0')

    for prize in prizes:
        cumulative += prize.probability
        if rand < float(cumulative):
            # 检查库存
            if prize.stock > 0:
                # 判断是否为"谢谢惠顾"类奖品
                is_thanks = '谢谢' in prize.name or '惠顾' in prize.name
                return prize, not is_thanks, False, progress_info

    # 未匹配到任何奖品，返回最后一个（通常是谢谢惠顾）
    last_prize = prizes[-1]
    if last_prize.stock > 0:
        is_thanks = '谢谢' in last_prize.name or '惠顾' in last_prize.name
        return last_prize, not is_thanks, False, progress_info

    return None, False, False, []


def calculate_win_rate(prizes: List[Prize]) -> dict:
    """
    计算活动中奖率

    Args:
        prizes: 奖品列表

    Returns:
        包含各奖品概率和总中奖率的字典
    """
    total_probability = sum(p.probability for p in prizes)

    return {
        "prizes": [{"name": p.name, "probability": float(p.probability)} for p in prizes],
        "total_win_rate": float(total_probability)
    }