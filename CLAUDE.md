# CLAUDE.md

本文件为「星梦智能分析系统」的项目开发指南，供 AI 编程助手与开发者共同遵循。

## 一、项目概述

星梦智能分析系统（产品名「星梦智能助手」）是一款 AI 应用，提供两大核心功能：

- **星座分析**：用户填写出生日期、性别、情感状态等，系统推算太阳星座并生成个性化报告
- **周公解梦**：用户填写梦境内容等信息，系统生成个性化梦境解读

需求文档与用户故事位于 `需求文档/`，页面原型位于 `原型图/星梦智能助手-页面原型.html`（开发前务必先阅读）。

## 二、技术栈

| 层 | 技术 |
|----|------|
| 前端 | 原生 HTML + CSS + JavaScript（ES6），基于原型图开发 |
| 后端 | Python 3.11+ / FastAPI |
| 数据库 | SQLite |
| AI 模型 | DeepSeek API（OpenAI 兼容接口） |
| 依赖管理 | uv |
| 测试 | pytest + httpx |

## 三、目录结构

```
E:\dreamchat\
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── main.py          # FastAPI 入口，挂载路由与静态文件
│   │   ├── config.py        # 配置读取（.env）
│   │   ├── db.py            # 数据库连接与初始化
│   │   ├── models.py        # ORM 数据模型
│   │   ├── schemas.py       # Pydantic 请求/响应模型
│   │   ├── deps.py          # 鉴权等公共依赖
│   │   ├── routers/         # 路由（auth / astro / dream / history）
│   │   └── services/        # 业务服务（ai.py / zodiac.py）
│   ├── pyproject.toml
│   └── .env                 # 环境变量（不入库）
├── frontend/                # 前端代码（从原型图复制并完善）
│   ├── index.html
│   ├── css/                 # 样式（从原型图提取，保持主题一致）
│   └── js/                  # 脚本（api / auth / astro / dream / history / main）
├── test/                    # 测试代码
├── 需求文档/                 # 需求文档与用户故事
├── 开发文档/                 # 接口文档、数据库设计等
└── 原型图/                   # 原型 HTML
```

## 四、环境准备与命令

```bash
# 首次安装依赖（在 backend/ 目录）
uv sync

# 启动开发服务器（默认 http://127.0.0.1:8000）
uv run uvicorn app.main:app --reload

# 运行测试
uv run pytest
```

后端依赖（pyproject.toml 声明）：`fastapi`、`uvicorn[standard]`、`sqlalchemy`、`pydantic`、`pydantic-settings`、`httpx`、`bcrypt`、`pyjwt`。

环境变量（backend/.env）：

```
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
DATABASE_URL=sqlite:///./data.db
```

## 五、架构约定

### 1. 接口规范

- 所有 API 统一前缀 `/api`，采用 RESTful 风格。
- 响应体统一为 `{"code": int, "message": str, "data": object|null}`。
- `code = 0` 表示成功；非 0 表示失败，`message` 为可直接展示给用户的提示文案。
- HTTP 状态码与 `code` 配合：成功 `200`，参数错误 `400`，未认证 `401`，资源不存在 `404`，服务端错误 `500`。

错误码分段约定：

| 段 | 含义 | 示例 |
|----|------|------|
| 0 | 成功 | — |
| 400xx | 参数/格式错误 | 40001 用户名格式错误 |
| 401xx | 认证错误 | 40101 未登录；40102 用户名或密码错误 |
| 404xx | 资源不存在 | 40401 记录不存在 |
| 500xx | 服务器/AI 错误 | 50001 AI 调用失败 |

### 2. 认证与鉴权

- 采用 **JWT（Bearer Token）**：登录/注册成功后在 `data` 中返回 `token` 与 `token_type`。
- 密码使用 **bcrypt** 哈希存储，任何接口不得返回密码或哈希。
- 「记住我」勾选 → token 有效期 **7 天**；不勾选 → 短期 token（如 24 小时），前端存 `sessionStorage`（浏览器关闭即失效）。
- 除注册/登录外的接口均需登录，通过 `Authorization: Bearer <token>` 携带凭证。

### 3. 数据隔离（硬性约束）

- **每个用户只能查看和操作自己的数据**。
- 所有涉及用户数据的查询/更新/删除，必须用当前登录用户的 `user_id` 过滤，禁止仅凭记录 `id` 直接操作。

### 4. AI 调用

- 通过 DeepSeek 的 OpenAI 兼容接口调用（`httpx` 客户端）。
- 单次请求**超时 10 秒**（需求要求响应 < 10 秒）。
- 调用失败或超时：返回 `50001` 与「生成失败，请稍后重试」，允许用户重试；**失败结果不写入数据库**。
- 星座类型由后端 `services/zodiac.py` 根据出生日期推算（含摩羯座跨年边界），不依赖 AI。

### 5. 数据库核心表

| 表 | 用途 |
|----|------|
| `users` | 用户（id、username、email、password_hash、created_at） |
| `constellation_records` | 星座分析记录（关联 user_id，存完整报告） |
| `dream_records` | 周公解梦记录（关联 user_id，存完整报告） |

详细字段与索引见 `开发文档/` 数据库设计文档。

## 六、代码风格

### Python
- 变量/函数名 `snake_case`，类名 `PascalCase`。
- 使用类型注解；Pydantic 定义请求/响应模型。
- 路由函数简洁，业务逻辑下沉到 `services/`。

### JavaScript
- 使用 ES6（`const`/`let`、箭头函数、模板字符串、`async/await`）。
- 变量/函数名 `camelCase`。
- 通过 `js/api.js` 统一封装 `fetch` 请求与错误处理，页面逻辑不直接拼接 URL。

### CSS
- 使用 **BEM** 命名规范（`block__element--modifier`）。
- 主题色与设计变量沿用原型图（深色星空主题），保持全站风格统一。

### HTML
- 使用语义化标签；页面文案使用中文。

## 七、关键约束

1. 前端必须基于 `原型图/星梦智能助手-页面原型.html` 开发，主题风格（深色星空）保持一致。
2. 接口响应格式统一 `{code, message, data}`，不得另起格式。
3. 数据隔离是硬性要求，任何跨用户数据访问都视为缺陷。
4. AI 失败/超时不落库，避免污染历史记录。
5. 开发接口文档、数据库设计文档后，放入 `开发文档/`，并保持与代码实现一致。
