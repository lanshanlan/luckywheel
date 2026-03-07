# 幸运轮盘抽奖小程序 - 开发方案

## 一、技术栈确认

| 层级 | 技术选型 |
|------|----------|
| 前端 | uni-app（Vue 3 + TypeScript） |
| 后端 | Python 3.14 + FastAPI |
| 数据库 | MySQL 8.4 LTS |
| ORM | SQLAlchemy 2.0 |
| 部署 | Nginx + Uvicorn |

---

## 二、功能需求

### 用户角色
- **参与者**：登录、参与抽奖、查看抽奖记录
- **发起者**：创建活动、设置奖品和概率、查看所有抽奖记录

### 核心功能
- 微信登录
- 活动列表展示
- 轮盘展示与旋转动画
- 抽奖逻辑（按概率随机抽取）
- 每人每个活动限抽一次
- 支持多个活动同时存在

---

## 三、数据库设计

### ER 关系图

```
用户(1) ──────< 抽奖记录(N)
                    │
活动(1) ────────────┤
                    │
活动(1) ──────< 奖品(N)
```

### 表结构

#### 1. 用户表 `users`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| openid | VARCHAR(64) | 微信用户唯一标识 |
| nickname | VARCHAR(64) | 昵称 |
| avatar_url | VARCHAR(255) | 头像地址 |
| created_at | DATETIME | 创建时间 |

#### 2. 活动表 `activities`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| title | VARCHAR(100) | 活动标题 |
| description | TEXT | 活动描述 |
| status | TINYINT | 0-未开始，1-进行中，2-已结束 |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |
| created_at | DATETIME | 创建时间 |

#### 3. 奖品表 `prizes`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| activity_id | INT | 关联活动ID |
| name | VARCHAR(100) | 奖品名称 |
| image_url | VARCHAR(255) | 奖品图片 |
| probability | DECIMAL(5,4) | 中奖概率（0-1） |
| stock | INT | 库存数量 |
| sort_order | INT | 轮盘显示顺序 |

#### 4. 抽奖记录表 `lottery_records`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| user_id | INT | 用户ID |
| activity_id | INT | 活动ID |
| prize_id | INT | 中奖奖品ID（未中奖为NULL） |
| is_won | TINYINT | 0-未中奖，1-中奖 |
| created_at | DATETIME | 抽奖时间 |

---

## 四、API 接口设计

### 用户模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 微信登录，返回token |

### 活动模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/activities | 获取活动列表 |
| GET | /api/activities/{id} | 获取活动详情（含奖品信息） |

### 抽奖模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/lottery/draw | 执行抽奖 |
| GET | /api/lottery/records | 查询我的抽奖记录 |
| GET | /api/lottery/check/{activity_id} | 检查是否已参与过某活动 |

### 管理模块（发起者使用）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/admin/activities | 创建活动 |
| PUT | /api/admin/activities/{id} | 修改活动 |
| DELETE | /api/admin/activities/{id} | 删除活动 |
| POST | /api/admin/prizes | 添加奖品 |
| PUT | /api/admin/prizes/{id} | 修改奖品 |
| DELETE | /api/admin/prizes/{id} | 删除奖品 |
| GET | /api/admin/records | 查询所有抽奖记录 |

---

## 五、项目目录结构

```
luckyWheel/
├── client/                          # uni-app 前端
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index/               # 首页-活动列表
│   │   │   │   └── index.vue
│   │   │   ├── lottery/             # 抽奖页-轮盘
│   │   │   │   └── index.vue
│   │   │   ├── record/              # 我的记录
│   │   │   │   └── index.vue
│   │   │   └── admin/               # 管理页
│   │   │       └── index.vue
│   │   ├── components/
│   │   │   └── LuckyWheel/          # 轮盘组件
│   │   │       └── LuckyWheel.vue
│   │   ├── api/
│   │   │   ├── index.ts             # 请求封装
│   │   │   ├── auth.ts              # 登录接口
│   │   │   ├── activity.ts          # 活动接口
│   │   │   └── lottery.ts           # 抽奖接口
│   │   ├── utils/
│   │   │   ├── request.ts           # 请求工具
│   │   │   └── auth.ts              # 登录工具
│   │   ├── store/                   # Pinia 状态管理
│   │   │   └── user.ts
│   │   ├── static/                  # 静态资源
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── pages.json               # 页面配置
│   │   └── manifest.json            # 应用配置
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── server/                          # Python 后端
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # 登录接口
│   │   │   ├── activity.py          # 活动接口
│   │   │   ├── lottery.py           # 抽奖接口
│   │   │   └── admin.py             # 管理接口
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── models.py            # ORM模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py           # Pydantic模型
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── lottery_service.py   # 抽奖核心逻辑
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── database.py          # 数据库连接
│   │   │   └── security.py          # JWT认证
│   │   └── __init__.py
│   ├── config.py                    # 配置文件
│   ├── main.py                      # 入口文件
│   └── requirements.txt             # 依赖
│
├── sql/
│   └── init.sql                     # 数据库初始化脚本
│
└── README.md
```

---

## 六、核心逻辑说明

### 抽奖概率算法

```python
import random

def draw_prize(prizes):
    """
    按概率随机抽取奖品
    prizes: 奖品列表，每个奖品有 probability 属性
    return: 中奖奖品或None（未中奖）
    """
    rand = random.random()  # 生成 0-1 的随机数
    cumulative = 0

    for prize in prizes:
        cumulative += prize.probability
        if rand < cumulative:
            return prize

    return None  # 未中奖
```

### 每人限抽一次逻辑

```python
def check_user_drawn(db, user_id, activity_id):
    """检查用户是否已参与过某活动"""
    record = db.query(LotteryRecord).filter(
        LotteryRecord.user_id == user_id,
        LotteryRecord.activity_id == activity_id
    ).first()

    return record is not None
```

---

## 七、开发计划

| 阶段 | 任务 | 说明 |
|------|------|------|
| 1. 后端搭建 | 创建项目、数据库建表、ORM模型、基础接口 | 配置 FastAPI + SQLAlchemy |
| 2. 核心接口 | 登录、活动查询、抽奖逻辑 | 实现核心业务 |
| 3. 前端开发 | 轮盘组件、页面开发、接口联调 | uni-app 开发 |
| 4. 管理功能 | 活动管理、奖品管理 | 管理后台 |
| 5. 部署上线 | 服务器部署、小程序提审 | Nginx + HTTPS |

---

## 八、前置准备

### 必须准备
- [ ] 微信小程序 AppID（去微信公众平台注册）
- [ ] 服务器 IP 和 SSH 访问权限
- [ ] 域名 + SSL 证书（小程序要求 HTTPS）
- [ ] 服务器安装 MySQL 8.4 LTS

### 开发环境
- [ ] Node.js 22+
- [ ] Python 3.14
- [ ] HBuilderX（uni-app 开发工具）
- [ ] 微信开发者工具

---

## 九、后端依赖

```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlalchemy>=2.0.0
pymysql>=1.1.0
pydantic>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
httpx>=0.24.0
```

---

## 十、前端依赖

```json
{
  "dependencies": {
    "@dcloudio/uni-app": "^3.0.0",
    "@dcloudio/uni-mp-weixin": "^3.0.0",
    "pinia": "^2.1.0",
    "vue": "^3.4.0"
  },
  "devDependencies": {
    "@dcloudio/vite-plugin-uni": "^3.0.0",
    "@dcloudio/uni-cli-shared": "^3.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```