# AI Agent 平台 — 项目文档

## 📋 项目概述

一个类似字节跳动扣子(Coze)的 AI Agent 平台，支持四大核心功能：**AI对话、文生图、图生图、声音克隆**。

- **后端**: Python FastAPI + SQLAlchemy（支持 SQLite/PostgreSQL）
- **前端**: React 19 + TypeScript + Vite + Tailwind CSS v4
- **架构**: 可插拔 Provider 模式，支持多 AI 提供商

---

## 🏗️ 项目结构

```
ai-agent-platform/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI 应用入口
│   │   ├── config.py             # 环境变量配置 (pydantic-settings)
│   │   ├── database.py           # SQLAlchemy 异步引擎
│   │   ├── models/models.py      # Conversation, Message, GenerationRecord
│   │   ├── schemas/schemas.py    # Pydantic 请求/响应模型
│   │   ├── api/                  # API 路由
│   │   │   ├── chat.py           # /api/chat (含 SSE 流式)
│   │   │   ├── image.py          # /api/images (文生图 + 图生图)
│   │   │   ├── voice.py          # /api/voice (声音克隆)
│   │   │   ├── files.py          # /api/files/upload 文件上传
│   │   │   └── providers.py      # /api/providers 提供商列表
│   │   ├── services/             # 业务逻辑层
│   │   │   ├── chat_service.py
│   │   │   ├── image_service.py
│   │   │   └── voice_service.py
│   │   ├── providers/            # 可插拔 AI 提供商
│   │   │   ├── base.py           # ABC 抽象基类
│   │   │   ├── chat/
│   │   │   │   ├── openai_chat.py        # OpenAI / 火山引擎 Ark
│   │   │   │   └── anthropic_chat.py     # Anthropic Claude
│   │   │   ├── image/
│   │   │   │   ├── openai_image.py       # OpenAI gpt-image (DALL-E 替代)
│   │   │   │   └── stability_image.py    # Stability AI
│   │   │   └── voice/
│   │   │       └── elevenlabs_voice.py   # ElevenLabs
│   │   └── utils/
│   │       └── file_storage.py   # 文件存储 (本地 / Supabase Storage)
│   ├── Procfile                  # Railway 部署配置
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx               # React Router 路由
│   │   ├── api/client.ts         # Axios API 客户端
│   │   ├── pages/
│   │   │   ├── ChatPage.tsx      # AI对话 (SSE 流式)
│   │   │   ├── TextToImagePage.tsx  # 文生图
│   │   │   ├── ImageToImagePage.tsx # 图生图
│   │   │   └── VoiceClonePage.tsx   # 声音克隆
│   │   └── components/
│   │       ├── Layout.tsx
│   │       └── Sidebar.tsx
│   ├── vercel.json               # Vercel SPA 路由
│   ├── vite.config.ts
│   └── package.json
└── .gitignore
```

---

## ✨ 已实现功能

### ✅ AI对话 (AI Chat)
- **提供商**: 火山引擎 Ark（OpenAI 兼容接口）
- **模型**: doubao-seed-1-6-flash-250615
- **流式响应**: SSE (Server-Sent Events) 实时输出
- **对话历史**: 数据库持久化，侧边栏历史列表

### ✅ 文生图 (Text-to-Image)
- **提供商**: Stability AI（Stable Image Core / Stable Image Ultra）
- **测试结果**: 已成功生成 1536x1536 图片

### ✅ 图生图 (Image-to-Image)
- **提供商**: Stability AI（Stable Image Core，支持 img2img）
- **状态**: 代码已实现，待测试

### ❌ 声音克隆 (Voice Clone)
- **提供商**: ElevenLabs
- **状态**: 代码已实现，需要配置 `ELEVENLABS_API_KEY`
- **注册**: https://elevenlabs.io

---

## 🔑 API 密钥配置

### 当前已配置的 Key
| 提供商 | 用途 | 状态 |
|--------|------|------|
| 火山引擎 Ark | AI对话 | ✅ 已配置 |
| Stability AI | 文生图 + 图生图 | ✅ 已配置 |
| OpenAI | gpt-image 文生图 | ⚠️ 额度不足 |
| ElevenLabs | 声音克隆 | ❌ 未配置 |

### 配置文件位置
- **本地开发**: `backend/.env`（已配置好，**不要提交到 Git**）
- **生产环境**: Railway 项目 Variables（见下文）

---

## ☁️ 部署配置

### GitHub 仓库
- **地址**: `https://github.com/hamiliu/ai-agent-platform`
- **分支**: `main`

### Supabase 项目
- **Project URL**: `https://nceylesyidpaorcgzgvx.supabase.co`
- **数据库**: `postgresql+asyncpg://postgres:28799bd5-4170-4352-b13d-3c3924c78ef4@db.nceylesyidpaorcgzgvx.supabase.co:6543/postgres`
- **Storage bucket**: `uploads`（Public）
- **service_role key**: 见 `.env` 文件

### Railway 环境变量（后端部署）
| 变量 | 值 |
|------|-----|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:密码@db.nceylesyidpaorcgzgvx.supabase.co:6543/postgres` |
| `SUPABASE_URL` | `https://nceylesyidpaorcgzgvx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | `eyJ...`（见 .env） |
| `SUPABASE_STORAGE_BUCKET` | `uploads` |
| `STABILITY_API_KEY` | `sk-JLfTmqkGRcjNOAbA5pUSChgWoklRG1jlrzMPkTWNTeMNddPk` |
| `OPENAI_API_KEY` | `ark-e66ca072-4dd7-480b-a02f-182e4dca0b19-97807` |
| `OPENAI_BASE_URL` | `https://ark.cn-beijing.volces.com/api/v3` |
| `OPENAI_IMAGE_API_KEY` | `sk-proj-U6l...` |
| `CORS_ORIGINS` | `["https://前端域名.vercel.app"]` |

### Vercel 环境变量（前端部署）
| 变量 | 值 |
|------|-----|
| `VITE_API_BASE_URL` | `https://后端域名.railway.app` |

---

## 🚀 部署步骤

### Railway 部署后端
1. 打开 [railway.app](https://railway.app)，用 GitHub 登录
2. **New Project** → **Deploy from GitHub repo** → 选 `hamiliu/ai-agent-platform`
3. **Settings** → **Root Directory** 设为 `backend`
4. **Variables** 添加上述环境变量
5. 部署后拿到域名（如 `xxx.railway.app`）

### Vercel 部署前端
1. 打开 [vercel.com](https://vercel.com)，用 GitHub 登录
2. **Add New** → **Project** → 选 `hamiliu/ai-agent-platform`
3. **Root Directory** 设为 `frontend`
4. **Environment Variables** 添加 `VITE_API_BASE_URL`
5. 部署后拿到域名（如 `xxx.vercel.app`）
6. 将域名填回 Railway 的 `CORS_ORIGINS`

---

## 🔧 本地开发

### 启动后端
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动前端
```bash
cd frontend
npm install
npm run dev
```

### Cloudflare Tunnel（外部访问）
```bash
cloudflared tunnel --protocol http2 --url http://localhost:5173
```

---

## 📝 当前状态

| 项目 | 状态 |
|------|------|
| 本地开发环境 | ✅ 运行中 |
| 代码托管 (GitHub) | ✅ 已推送 |
| Supabase 数据库 | ✅ 已创建 |
| Supabase Storage | ✅ 已创建 |
| Railway 部署 | ❌ 未部署 |
| Vercel 部署 | ❌ 未部署 |
| 声音克隆 | ❌ 需 ElevenLabs Key |

---

## 👤 联系方式

- **GitHub**: [hamiliu](https://github.com/hamiliu)
- **项目仓库**: [ai-agent-platform](https://github.com/hamiliu/ai-agent-platform)
