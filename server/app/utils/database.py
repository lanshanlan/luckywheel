from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, SmallInteger
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

from config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    openid = Column(String(64), unique=True, index=True, nullable=False, comment="微信用户唯一标识")
    nickname = Column(String(64), comment="昵称")
    avatar_url = Column(String(255), comment="头像地址")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    lottery_records = relationship("LotteryRecord", back_populates="user")


class Activity(Base):
    """活动表"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False, comment="活动标题")
    description = Column(Text, comment="活动描述")
    status = Column(SmallInteger, default=1, comment="状态：0-未开始，1-进行中，2-已结束")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    prizes = relationship("Prize", back_populates="activity", cascade="all, delete-orphan")
    lottery_records = relationship("LotteryRecord", back_populates="activity")


class Prize(Base):
    """奖品表"""
    __tablename__ = "prizes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, comment="关联活动ID")
    name = Column(String(100), nullable=False, comment="奖品名称")
    image_url = Column(String(255), comment="奖品图片")
    probability = Column(DECIMAL(5, 4), nullable=False, comment="中奖概率（0-1）")
    stock = Column(Integer, default=0, comment="库存数量")
    sort_order = Column(Integer, default=0, comment="轮盘显示顺序")

    # 关系
    activity = relationship("Activity", back_populates="prizes")
    lottery_records = relationship("LotteryRecord", back_populates="prize")


class LotteryRecord(Base):
    """抽奖记录表"""
    __tablename__ = "lottery_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False, comment="活动ID")
    prize_id = Column(Integer, ForeignKey("prizes.id"), nullable=True, comment="中奖奖品ID")
    is_won = Column(SmallInteger, default=0, comment="是否中奖：0-未中奖，1-中奖")
    created_at = Column(DateTime, default=datetime.now, comment="抽奖时间")

    # 关系
    user = relationship("User", back_populates="lottery_records")
    activity = relationship("Activity", back_populates="lottery_records")
    prize = relationship("Prize", back_populates="lottery_records")