"""
API 接口测试
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """健康检查测试"""

    def test_root(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health(self, client):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestActivityAPI:
    """活动接口测试"""

    def test_get_activities_empty(self, client):
        """测试获取空活动列表"""
        response = client.get("/api/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_activities_with_data(self, client, test_activity):
        """测试获取活动列表"""
        response = client.get("/api/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "测试活动"

    def test_get_activity_detail(self, client, test_activity, test_prizes):
        """测试获取活动详情"""
        response = client.get(f"/api/activities/{test_activity.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "测试活动"
        assert "prizes" in data
        assert len(data["prizes"]) == 3

    def test_get_activity_not_found(self, client):
        """测试获取不存在的活动"""
        response = client.get("/api/activities/99999")
        assert response.status_code == 404


class TestLotteryAPI:
    """抽奖接口测试"""

    def test_draw_without_auth(self, client, test_activity):
        """测试未登录抽奖"""
        response = client.post(
            "/api/lottery/draw",
            json={"activity_id": test_activity.id}
        )
        assert response.status_code == 401  # 未认证返回 401

    def test_draw_with_auth(self, client, test_activity, test_prizes, auth_headers):
        """测试登录后抽奖"""
        response = client.post(
            "/api/lottery/draw",
            json={"activity_id": test_activity.id},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "is_won" in data
        assert "message" in data

    def test_draw_twice_same_activity(self, client, test_activity, test_prizes, auth_headers):
        """测试同一活动重复抽奖"""
        # 第一次抽奖
        response1 = client.post(
            "/api/lottery/draw",
            json={"activity_id": test_activity.id},
            headers=auth_headers
        )
        assert response1.status_code == 200

        # 第二次抽奖应该失败
        response2 = client.post(
            "/api/lottery/draw",
            json={"activity_id": test_activity.id},
            headers=auth_headers
        )
        assert response2.status_code == 400
        assert "已参与过" in response2.json()["detail"]

    def test_draw_nonexistent_activity(self, client, auth_headers):
        """测试抽奖不存在的活动"""
        response = client.post(
            "/api/lottery/draw",
            json={"activity_id": 99999},
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_check_drawn_false(self, client, test_activity, auth_headers):
        """测试检查未抽奖状态"""
        response = client.get(
            f"/api/lottery/check/{test_activity.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["has_drawn"] == False

    def test_check_drawn_true(self, client, test_activity, test_prizes, auth_headers):
        """测试检查已抽奖状态"""
        # 先抽奖
        client.post(
            "/api/lottery/draw",
            json={"activity_id": test_activity.id},
            headers=auth_headers
        )

        # 再检查
        response = client.get(
            f"/api/lottery/check/{test_activity.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["has_drawn"] == True
        assert data["record"] is not None

    def test_get_records_empty(self, client, auth_headers):
        """测试获取空抽奖记录"""
        response = client.get("/api/lottery/records", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_records_with_data(self, client, test_activity, test_prizes, auth_headers):
        """测试获取抽奖记录"""
        # 先抽奖
        client.post(
            "/api/lottery/draw",
            json={"activity_id": test_activity.id},
            headers=auth_headers
        )

        # 获取记录
        response = client.get("/api/lottery/records", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestAdminAPI:
    """管理接口测试"""

    def test_create_activity(self, client, auth_headers):
        """测试创建活动"""
        response = client.post(
            "/api/admin/activities",
            json={
                "title": "新活动",
                "description": "新活动描述",
                "status": 1
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "新活动"

    def test_update_activity(self, client, test_activity, auth_headers):
        """测试更新活动"""
        response = client.put(
            f"/api/admin/activities/{test_activity.id}",
            json={"title": "更新后的活动"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新后的活动"

    def test_delete_activity(self, client, test_activity, auth_headers):
        """测试删除活动"""
        response = client.delete(
            f"/api/admin/activities/{test_activity.id}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_create_prize(self, client, test_activity, auth_headers):
        """测试创建奖品"""
        response = client.post(
            "/api/admin/prizes",
            json={
                "activity_id": test_activity.id,
                "name": "测试奖品",
                "probability": 0.5,
                "stock": 100
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "测试奖品"

    def test_get_all_records(self, client, test_activity, test_prizes, auth_headers):
        """测试获取所有抽奖记录"""
        # 先抽奖
        client.post(
            "/api/lottery/draw",
            json={"activity_id": test_activity.id},
            headers=auth_headers
        )

        # 获取所有记录
        response = client.get("/api/admin/records", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1