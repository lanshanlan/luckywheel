from pydantic_settings import BaseSettings
from typing import Optional
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "幸运轮盘抽奖系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "your_password"
    DB_NAME: str = "lucky_wheel"

    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24 * 7  # 7天

    # 微信小程序配置
    WX_APPID: str = "wx009870b78b1f50fb"
    WX_SECRET: str = "44e6b233e1dfdfa8f4f65fc40d3338e0"

    @property
    def DATABASE_URL(self) -> str:
        # 对用户名和密码进行 URL 编码，避免 @ 等特殊字符导致解析错误
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return f"mysql+pymysql://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return f"mysql+aiomysql://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()