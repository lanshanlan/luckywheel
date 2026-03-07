"""
模型测试
"""
import pytest
from datetime import datetime

from app.utils.database import User, Activity, Prize, LotteryRecord


class TestModels:
    """数据库模型测试"""

    def test_user_model(self, db_session):
        """测试用户模型"""
        user = User(
            openid="test_openid",
            nickname="测试用户",
            avatar_url="https://example.com/avatar.png"
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.openid == "test_openid"
        assert user.nickname == "测试用户"
        assert user.created_at is not None

    def test_activity_model(self, db_session):
        """测试活动模型"""
        activity = Activity(
            title="测试活动",
            description="活动描述",
            status=1
        )
        db_session.add(activity)
        db_session.commit()

        assert activity.id is not None
        assert activity.title == "测试活动"
        assert activity.status == 1
        assert activity.created_at is not None

    def test_prize_model(self, db_session):
        """测试奖品模型"""
        # 先创建活动
        activity = Activity(title="活动")
        db_session.add(activity)
        db_session.commit()

        prize = Prize(
            activity_id=activity.id,
            name="测试奖品",
            probability=0.1,
            stock=100,
            sort_order=1
        )
        db_session.add(prize)
        db_session.commit()

        assert prize.id is not None
        assert prize.name == "测试奖品"
        assert float(prize.probability) == 0.1

    def test_lottery_record_model(self, db_session):
        """测试抽奖记录模型"""
        # 创建相关数据
        user = User(openid="test_openid")
        activity = Activity(title="活动")
        db_session.add_all([user, activity])
        db_session.commit()

        record = LotteryRecord(
            user_id=user.id,
            activity_id=activity.id,
            prize_id=None,
            is_won=0
        )
        db_session.add(record)
        db_session.commit()

        assert record.id is not None
        assert record.is_won == 0
        assert record.created_at is not None

    def test_activity_prize_relationship(self, db_session):
        """测试活动奖品关系"""
        activity = Activity(title="活动")
        db_session.add(activity)
        db_session.commit()

        prize1 = Prize(activity_id=activity.id, name="奖品1", probability=0.5)
        prize2 = Prize(activity_id=activity.id, name="奖品2", probability=0.5)
        db_session.add_all([prize1, prize2])
        db_session.commit()

        # 测试关系
        db_session.refresh(activity)
        assert len(activity.prizes) == 2

    def test_user_lottery_record_relationship(self, db_session):
        """测试用户抽奖记录关系"""
        user = User(openid="test_openid")
        activity = Activity(title="活动")
        db_session.add_all([user, activity])
        db_session.commit()

        record = LotteryRecord(
            user_id=user.id,
            activity_id=activity.id,
            is_won=1
        )
        db_session.add(record)
        db_session.commit()

        # 测试关系
        db_session.refresh(user)
        assert len(user.lottery_records) == 1