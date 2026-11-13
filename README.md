# 星梦智能助手（dreamchat）

一款基于大模型的 AI 应用，提供**星座分析**与**周公解梦**两大功能。用户登录后填写信息，即可获得个性化的 AI 分析报告，并支持历史记录的查看与管理。

## ✨ 功能特性

- **用户注册 / 登录**：JWT 认证，支持「记住我」（7 天免登录），密码 bcrypt 加密存储
- **星座分析**：根据出生日期推算太阳星座，AI 生成性格、运势、幸运色/幸运数字、建议等个性化报告
- **周公解梦**：根据梦境描述，AI 生成核心寓意、针对性解读、生活建议与整体评价
- **历史记录**：分「星座分析 / 周公解梦」两类查看，支持详情、删除单条、清空，分页加载
- **数据隔离**：每个用户只能查看和操作自己的数据

## 🛠 技术栈

| 层 | 技术 |
|----|------|
| 前端 | 原生 HTML + CSS + JavaScript（ES6），深色星空主题 |
| 后端 | Python 3.11+ / FastAPI |
| 数据库 | SQLite + SQLAlchemy 2.0 |
| AI 模型 | DeepSeek API（OpenAI 兼容接口） |
| 依赖管理 | uv |
| 测试 | pytest |

## 📁 目录结构

```
dreamchat/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 配置读取（.env）
│   │   ├── db.py            # 数据库连接
│   │   ├── models.py        # ORM 数据模型
│   │   ├── schemas.py       # Pydantic 请求/响应模型
│   │   ├── deps.py          # 鉴权等公共依赖
│   │   ├── routers/         # 路由（auth / astro / dream / history）
│   │   └── services/        # 业务服务（ai.py / zodiac.py）
│   ├── test/                # 自动化测试
│   ├── create_db.py         # 手动建库脚本（可选）
│   └── pyproject.toml
├── frontend/                # 前端页面
│   ├── login.html           # 登录/注册
│   ├── index.html           # 主页面
│   ├── astro.html           # 星座分析
│   ├── dream.html           # 周公解梦
│   └── history.html         # 历史记录
├── 需求文档/                 # 需求文档与用户故事
├── 开发文档/                 # 接口文档、数据库设计、业务术语表
└── 原型图/                   # 页面原型
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)（依赖管理）

### 1. 安装依赖

```bash
cd backend
uv sync
```

### 2. 配置环境变量

在 `backend/` 下创建 `.env` 文件（参考下方「配置说明」），填入 DeepSeek API Key：

```bash
DEEPSEEK_API_KEY=sk-你的密钥
```

### 3. 启动服务

```bash
cd backend
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

启动后浏览器访问：**http://127.0.0.1:8000/login.html**

> 首次启动会自动建表，并创建测试账号 `admin / 123456`。

### 4. 运行测试

```bash
cd backend
uv run pytest
```

## 🔌 API 接口

统一响应格式：`{code, message, data}`，`code = 0` 表示成功。

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录（返回 JWT） |
| POST | /api/astro/analyze | 星座分析（需登录） |
| POST | /api/dream/analyze | 周公解梦（需登录） |
| GET | /api/history | 历史记录列表（分页） |
| GET | /api/history/{id} | 历史记录详情 |
| DELETE | /api/history/{id} | 删除单条记录 |
| DELETE | /api/history | 清空某类记录 |

完整接口说明见 `开发文档/接口文档.md`。

## ⚙️ 配置说明

`backend/.env` 支持以下环境变量：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DEEPSEEK_API_KEY | DeepSeek API 密钥（必填） | 空 |
| DEEPSEEK_BASE_URL | API 地址 | https://api.deepseek.com |
| DEEPSEEK_MODEL | 模型名称 | deepseek-chat |
| JWT_SECRET_KEY | JWT 签名密钥 | 开发默认值 |
| DATABASE_URL | 数据库连接串 | sqlite:///./star_dream.db |

## 📚 项目文档

- 需求文档：`需求文档/`（含各功能需求描述与 PRD、用户故事）
- 接口文档：`开发文档/接口文档.md`
- 数据库设计：`开发文档/数据库设计.md`
- 业务术语表：`开发文档/业务术语表.md`
- 页面原型：`原型图/星梦智能助手-页面原型.html`

## 📝 许可证

MIT License
