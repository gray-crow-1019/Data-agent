# Data Analyst Agent

这是一个用于数据分析 Agent 的全栈脚手架：后端基于 FastAPI，前端基于 React + Vite + Tailwind。配置统一在 `.env.example` 中定义，通过环境变量注入用于本地开发或 CI/CD。

## 架构
- `apps/api`：FastAPI 后端，包含编排状态机、语义层、治理、工具适配器。
- `apps/web`：React 前端，包含对话、任务详情与元数据浏览。
- `packages/contracts`：前后端共享 DTO 与卡片协议。
- `infra`：可选部署资产（nginx、k8s 占位）。

## 快速开始
1. 确保 Python 3.11+ 与 Node 18+ 可用。
2. 从 `.env.example` 提供本地开发所需环境变量。
3. （可选）运行 `docker-compose up db redis` 启动 Postgres/Redis。
4. 启动后端：
   - `pip install -r apps/api/requirements.txt`
   - `uvicorn main:app --reload --host 0.0.0.0 --port 8000`（在 `apps/api/src` 目录执行）
5. 启动前端：
   - `pnpm -C apps/web install`
   - `pnpm -C apps/web dev`

## 后端接口
- `POST /chat` -> 运行编排并返回任务结果
- `GET /tasks` -> 列出最近任务
- `GET /tasks/{id}` -> 获取任务 spec + result
- `POST /tasks/{id}/rerun` -> 复跑上次参数
- `GET /metrics` / `GET /dimensions` / `GET /catalog`
- `GET /health`

## 环境变量
完整列表请见 `.env.example`，关键项包括：
- `AUTH_TOKEN`：简易 Bearer 鉴权
- `DATABASE_URL`：任务持久化（占位）
- `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`（或 DashScope 变量）
- `LLM_STRICT_JSON`：是否强制 LLM 输出 JSON（false 更自由但更不稳定）
- `DASHSCOPE_API_KEY`, `DASHSCOPE_BASE_URL`
- `CLICKHOUSE_URL`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, `CLICKHOUSE_DATABASE`（当 `SQL_ENGINE=clickhouse`）
- `VITE_API_BASE_URL`：前端 API 地址
- `VITE_WEB_PORT`：前端开发端口
- `UPLOADS_DIR`, `MAX_UPLOAD_MB`：上传目录与大小限制
- `MIN_GROUP_SIZE`, `MAX_SCAN_BYTES`, `RATE_LIMIT_RPS`：治理阈值

## 备注
- 编排状态在 `apps/api/src/orchestrator/states` 中模块化。
- 可在 `apps/api/src/tools/sql/runner.py` 替换真实数仓执行。
- UI 使用自定义主题与简单 mock 数据。
