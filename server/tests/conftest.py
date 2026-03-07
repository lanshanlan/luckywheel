# 后端测试配置
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 使用内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 在导入 app 之前覆盖数据库 engine
import app.utils.database as db_module
db_module.engine = test_engine

from main import app
from app.utils.database import Base, get_db, User, Activity, Prize, LotteryRecord


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# 覆盖应用的数据库依赖
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 创建所有表
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 清理所有表
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client():
    """创建测试客户端"""
    Base.metadata.create_all(bind=test_engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def test_user(db_session):
    """创建测试用户"""
    user = User(
        openid="test_openid_123",
        nickname="测试用户",
        avatar_url="https://example.com/avatar.png"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_activity(db_session):
    """创建测试活动"""
    activity = Activity(
        id=1,
        title="测试活动",
        description="这是一个测试活动",
        status=1
    )
    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)
    return activity


@pytest.fixture(scope="function")
def test_prizes(db_session, test_activity):
    """创建测试奖品"""
    prizes = [
        Prize(
            activity_id=test_activity.id,
            name="一等奖",
            probability=0.1,
            stock=10,
            sort_order=1
        ),
        Prize(
            activity_id=test_activity.id,
            name="二等奖",
            probability=0.2,
            stock=20,
            sort_order=2
        ),
        Prize(
            activity_id=test_activity.id,
            name="谢谢参与",
            probability=0.7,
            stock=1000,
            sort_order=3
        )
    ]
    db_session.add_all(prizes)
    db_session.commit()
    return prizes


@pytest.fixture
def auth_headers(test_user):
    """生成认证头"""
    from app.utils.security import create_access_token
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}