"""
抽奖核心逻辑服务
"""
import random
from decimal import Decimal
from typing import Optional, List, Tuple

from app.utils.database import Prize


def draw_prize(prizes: List[Prize]) -> Tuple[Optional[Prize], bool]:
    """
    按概率随机抽取奖品

    算法说明：
    1. 生成一个 0-1 之间的随机数
    2. 按奖品顺序累加概率
    3. 当随机数小于累计概率时，返回该奖品

    Args:
        prizes: 奖品列表，每个奖品有 probability 属性

    Returns:
        (中奖奖品, 是否真正中奖)
        - 如果是普通奖品，返回 (prize, True)
        - 如果是"谢谢惠顾"奖品，返回 (prize, False)
        - 如果没有匹配的奖品，返回 (None, False)
    """
    if not prizes:
        return None, False

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
                return prize, not is_thanks

    # 未匹配到任何奖品，返回最后一个（通常是谢谢惠顾）
    last_prize = prizes[-1]
    if last_prize.stock > 0:
        is_thanks = '谢谢' in last_prize.name or '惠顾' in last_prize.name
        return last_prize, not is_thanks

    return None, False


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