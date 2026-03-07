from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, activity, lottery, admin
from app.utils.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="幸运轮盘抽奖系统",
    description="微信小程序抽奖后端API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])
app.include_router(activity.router, prefix="/api/activities", tags=["活动"])
app.include_router(lottery.router, prefix="/api/lottery", tags=["抽奖"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理"])


@app.get("/")
async def root():
    return {"message": "幸运轮盘抽奖系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}