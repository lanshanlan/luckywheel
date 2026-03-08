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

---

## 十一、启动方式

### 1. 数据库启动

#### 安装 MySQL 8.4 LTS

**macOS (Homebrew):**
```bash
brew install mysql
brew services start mysql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

**Windows:**
下载 MySQL Installer: https://dev.mysql.com/downloads/installer/

#### 初始化数据库

```bash
# 登录 MySQL
mysql -u root -p

# 执行初始化脚本
source sql/init.sql

# 或者直接执行
mysql -u root -p < sql/init.sql
```

#### 验证数据库

```bash
mysql -u root -p
```

```sql
USE lucky_wheel;
SHOW TABLES;
SELECT * FROM activities;
```

---

### 2. 后端启动

#### 创建虚拟环境

```bash
cd server

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 配置环境变量

创建 `server/.env` 文件：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=lucky_wheel

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=168

# 微信小程序配置
WX_APPID=your_appid
WX_SECRET=your_secret
```

#### 启动服务

```bash
# 开发模式（热重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 验证后端

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

---

### 3. 前端启动

#### 安装依赖

```bash
cd client
npm install
```

#### 开发模式

```bash
# 微信小程序
npm run dev:mp-weixin

# H5
npm run dev:h5
```

#### 构建生产版本

```bash
# 微信小程序
npm run build:mp-weixin

# H5
npm run build:h5
```

#### 预览小程序

1. 打开**微信开发者工具**
2. 导入项目，选择 `client/dist/dev/mp-weixin` 目录
3. 填写 AppID（可在 manifest.json 中配置）
4. 点击预览或真机调试

---

### 4. 完整启动流程

```bash
# 1. 启动数据库
mysql.server start  # macOS
# 或 sudo systemctl start mysql  # Linux

# 2. 初始化数据库（首次运行）
mysql -u root -p < sql/init.sql

# 3. 启动后端
cd server
source venv/bin/activate
uvicorn main:app --reload --port 8000

# 4. 启动前端（新终端）
cd client
npm install
npm run dev:mp-weixin

# 5. 微信开发者工具打开 client/dist/dev/mp-weixin
```

---

### 5. 常见问题

#### 数据库连接失败

检查 `server/.env` 中的数据库配置是否正确：
```bash
mysql -u root -p -e "SELECT 1"
```

#### 前端请求后端失败

1. 确认后端已启动: http://localhost:8000/health
2. 检查 `client/src/api/index.ts` 中的 `BASE_URL` 是否正确
3. 微信开发者工具中勾选「不校验合法域名」

#### npm install 失败

```bash
# 清除缓存重试
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## 十二、阿里云服务器部署流程

### 1. 服务器准备

#### 购买阿里云 ECS 服务器
- 选择配置：建议 2核4G 起
- 操作系统：Ubuntu 22.04 或 CentOS 7/8
- 购买时开放安全组端口：22(SSH)、80(HTTP)、443(HTTPS)、3306(MySQL)

#### 连接服务器
```bash
ssh root@你的服务器IP
```

---

### 2. 环境安装

#### 更新系统
```bash
# Ubuntu
apt update && apt upgrade -y

# CentOS
yum update -y
```

#### 安装 Python 3.14
```bash
# Ubuntu
apt install -y python3.14 python3.14-venv python3-pip

# 或使用 pyenv 安装（推荐，更灵活）
curl https://pyenv.run | bash
pyenv install 3.14.0
pyenv global 3.14.0
```

#### 安装 MySQL 8.4
```bash
# Ubuntu
apt install -y mysql-server mysql-client

# 启动并设置开机自启
systemctl start mysql
systemctl enable mysql

# 安全配置
mysql_secure_installation
```

#### 安装 Nginx
```bash
apt install -y nginx
systemctl start nginx
systemctl enable nginx
```

---

### 3. 数据库配置

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE lucky_wheel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lucky_user'@'localhost' IDENTIFIED BY '你的强密码';
GRANT ALL PRIVILEGES ON lucky_wheel.* TO 'lucky_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

### 4. 部署后端代码

#### 创建应用目录
```bash
mkdir -p /var/www/luckywheel
cd /var/www/luckywheel
```

#### 上传代码（选择一种方式）

**方式一：Git 拉取**
```bash
apt install -y git
git clone 你的仓库地址 .
```

**方式二：SCP 上传**
```bash
# 在本地执行
scp -r server/* root@服务器IP:/var/www/luckywheel/
```

#### 创建虚拟环境并安装依赖
```bash
cd /var/www/luckywheel/server
python3.14 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 配置环境变量
```bash
# 创建生产环境配置
cat > /var/www/luckywheel/server/.env << 'EOF'
DB_HOST=localhost
DB_PORT=3306
DB_USER=lucky_user
DB_PASSWORD=你的强密码
DB_NAME=lucky_wheel

JWT_SECRET_KEY=生成一个复杂的密钥
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=168

WX_APPID=your_appid
WX_SECRET=your_secret
EOF

# 生成安全密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 5. 配置 Systemd 服务

```bash
cat > /etc/systemd/system/luckywheel.service << 'EOF'
[Unit]
Description=Lucky Wheel FastAPI Application
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/luckywheel/server
Environment="PATH=/var/www/luckywheel/server/venv/bin"
ExecStart=/var/www/luckywheel/server/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 设置权限
chown -R www-data:www-data /var/www/luckywheel

# 启动服务
systemctl daemon-reload
systemctl start luckywheel
systemctl enable luckywheel
```

---

### 6. 配置 Nginx 反向代理

```bash
cat > /etc/nginx/sites-available/luckywheel << 'EOF'
server {
    listen 80;
    server_name 你的域名或IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/luckywheel /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

---

### 7. 配置 HTTPS（推荐）

```bash
# 安装 Certbot
apt install -y certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d 你的域名

# 自动续期
systemctl enable certbot.timer
```

---

### 8. 防火墙配置

```bash
# Ubuntu (UFW)
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable

# 阿里云安全组也要开放这些端口
```

---

### 9. 验证部署

```bash
# 检查服务状态
systemctl status luckywheel
systemctl status nginx

# 测试 API
curl http://localhost:8000/health
curl http://你的域名/
```

---

### 10. 常用运维命令

| 操作 | 命令 |
|------|------|
| 查看日志 | `journalctl -u luckywheel -f` |
| 重启服务 | `systemctl restart luckywheel` |
| 查看状态 | `systemctl status luckywheel` |
| 更新代码 | `git pull && systemctl restart luckywheel` |