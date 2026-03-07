"""
抽奖服务测试
"""
import pytest
from decimal import Decimal

from app.services.lottery_service import draw_prize, calculate_win_rate
from app.utils.database import Prize


class TestLotteryService:
    """抽奖服务测试"""

    def test_draw_prize_empty_list(self):
        """测试空奖品列表"""
        result = draw_prize([])
        assert result is None

    def test_draw_prize_single_prize(self, mocker):
        """测试单个奖品必中"""
        # 模拟随机数为0.05（小于0.1）
        mocker.patch('random.random', return_value=0.05)

        prize = Prize(
            id=1,
            activity_id=1,
            name="一等奖",
            probability=Decimal('0.1'),
            stock=10
        )

        result = draw_prize([prize])
        assert result == prize

    def test_draw_prize_second_prize(self, mocker):
        """测试抽中第二个奖品"""
        # 模拟随机数为0.15（在0.1-0.3之间）
        mocker.patch('random.random', return_value=0.15)

        prizes = [
            Prize(id=1, activity_id=1, name="一等奖", probability=Decimal('0.1'), stock=10),
            Prize(id=2, activity_id=1, name="二等奖", probability=Decimal('0.2'), stock=20),
            Prize(id=3, activity_id=1, name="谢谢参与", probability=Decimal('0.7'), stock=1000)
        ]

        result = draw_prize(prizes)
        assert result.name == "二等奖"

    def test_draw_prize_no_stock(self, mocker):
        """测试奖品无库存"""
        mocker.patch('random.random', return_value=0.05)

        prizes = [
            Prize(id=1, activity_id=1, name="一等奖", probability=Decimal('0.1'), stock=0)
        ]

        result = draw_prize(prizes)
        # 库存为0，无法中奖
        assert result is None

    def test_draw_prize_probability_distribution(self):
        """测试概率分布（运行多次验证）"""
        prizes = [
            Prize(id=1, activity_id=1, name="一等奖", probability=Decimal('0.1'), stock=1000),
            Prize(id=2, activity_id=1, name="二等奖", probability=Decimal('0.2'), stock=1000),
            Prize(id=3, activity_id=1, name="谢谢参与", probability=Decimal('0.7'), stock=1000)
        ]

        results = {"一等奖": 0, "二等奖": 0, "谢谢参与": 0}
        runs = 10000

        for _ in range(runs):
            result = draw_prize(prizes)
            if result:
                results[result.name] += 1

        # 验证概率大致符合预期（允许一定误差）
        first_rate = results["一等奖"] / runs
        second_rate = results["二等奖"] / runs
        thanks_rate = results["谢谢参与"] / runs

        # 允许 5% 的误差
        assert abs(first_rate - 0.1) < 0.05
        assert abs(second_rate - 0.2) < 0.05
        assert abs(thanks_rate - 0.7) < 0.05

    def test_calculate_win_rate(self):
        """测试中奖率计算"""
        prizes = [
            Prize(id=1, activity_id=1, name="一等奖", probability=Decimal('0.1'), stock=10),
            Prize(id=2, activity_id=1, name="二等奖", probability=Decimal('0.2'), stock=20)
        ]

        result = calculate_win_rate(prizes)

        assert len(result["prizes"]) == 2
        assert result["total_win_rate"] == 0.3

    def test_draw_prize_high_probability(self, mocker):
        """测试高概率奖品必中"""
        mocker.patch('random.random', return_value=0.99)

        prizes = [
            Prize(id=1, activity_id=1, name="大奖", probability=Decimal('1.0'), stock=100)
        ]

        result = draw_prize(prizes)
        assert result is not None
        assert result.name == "大奖"