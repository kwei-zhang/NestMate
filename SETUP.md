# NestMate — 本地运行

多伦多/安省华人找室友平台。前后端分离：FastAPI + React。

## 架构概览

- **数据来源**：半自动 + 人工审核。站长在 `/admin` 贴入小红书帖子链接/正文 → OpenAI 抽取结构化字段 → 人工审核发布。
- **失效检测**：每日定时任务（404 即归档 / Last-Modified 变化交 AI 判断 / 超 1 个月归档）。
- **联系方式门禁**：只在登录后经 `GET /listings/{id}/contact` 返回；公开列表/详情绝不含联系方式。
- **登录**：Google OAuth + 微信登录（无邮箱/密码注册）。

## 1. 启动数据库

```bash
docker compose up -d db
```

## 2. 后端（FastAPI）

```bash
cd backend
cp .env.example .env          # 填入 OPENAI_API_KEY / OAuth 凭据 / ADMIN_EMAILS
uv venv --python 3.12 .venv
uv pip install -e ".[dev]" --python .venv
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

- API 文档：http://localhost:8000/docs
- 跑测试：`.venv/bin/pytest`

> 设为管理员：把你的 Google 邮箱加入 `.env` 的 `ADMIN_EMAILS`，首次登录即获得 admin 角色，可访问 `/admin`。

## 3. 前端（React + Vite）

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173 ，/api 自动代理到后端
```

## 4. 端到端验证

1. 浏览首页 → 用 FilterBar 按地区/预算/MBTI/宠物筛选。
2. 进入房源详情 → 未登录时联系方式被遮挡。
3. 用 Google/微信登录 → 回到详情可查看联系方式、收藏。
4. `/post/new` 发帖 → 进入待审核。
5. 管理员 `/admin` 贴小红书正文 → AI 抽取草稿 → 发布 → 首页可见。

## 关键目录

- `backend/app/services/ai_extract.py` — OpenAI 结构化抽取
- `backend/app/services/staleness.py` — 失效检测定时任务
- `backend/app/services/oauth.py` — Google/微信 OAuth
- `backend/app/api/` — auth / listings / favorites / admin 路由
- `frontend/src/pages/` — 页面；`frontend/src/components/ContactGate.tsx` — 联系方式门禁
