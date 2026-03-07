"""
安全模块测试
"""
import pytest
from datetime import timedelta

from app.utils.security import create_access_token, verify_token


class TestSecurity:
    """安全模块测试"""

    def test_create_access_token(self):
        """测试创建 JWT token"""
        data = {"sub": "123"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)

    def test_create_access_token_with_expiry(self):
        """测试创建带过期时间的 token"""
        data = {"sub": "123"}
        expires = timedelta(hours=1)
        token = create_access_token(data, expires)

        assert token is not None

    def test_verify_valid_token(self):
        """测试验证有效 token"""
        data = {"sub": "123"}
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"

    def test_verify_invalid_token(self):
        """测试验证无效 token"""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token)
        assert payload is None

    def test_verify_empty_token(self):
        """测试验证空 token"""
        payload = verify_token("")
        assert payload is None