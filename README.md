# Data Analyst Agent

这是一个用于数据分析 Agent 的全栈脚手架：后端基于 FastAPI，前端基于 React + Vite + Tailwind。配置统一在 `.env.example` 中定义，通过环境变量注入用于本地开发或 CI/CD。

## 项目简介
Data Analyst Agent 旨在把“数据上传 → 语义理解 → 任务编排 → 查询执行 → 结果表达”串成一条可复用的链路。它不是单一的聊天接口，而是一套可落地的分析工作流框架，兼顾工程化、可扩展和可治理。

## 创新点
- **状态机式编排**：将分析流程拆解为可组合的状态（分析、澄清、规划、执行、叙述等），便于插拔与治理。
- **语义层 + 协议化卡片**：语义模型抽象指标/维度，前后端通过共享 DTO 与卡片协议对齐，降低“模型输出不稳定”带来的前端适配成本。
- **多引擎可切换**：同时支持 sqlite 与 ClickHouse，SQL Runner 可替换为真实数仓执行。
- **安全与治理内置**：包含最小分组、扫描阈值、速率限制、导出控制等治理策略，默认可用。
- **工具化扩展**：SQL、Python 分析、可视化与导出均以工具模块形式组织，易于替换或新增。

## 核心优势
- **全栈一体**：前后端同仓库、同协议、同环境变量体系，启动与部署成本低。
- **低耦合高可维护**：按模块划分（编排、语义、治理、工具、持久化），便于团队协作与扩展。
- **面向真实业务**：支持上传数据集、自动建表、检索与下载，覆盖“从数据到洞察”的完整闭环。
- **工程友好**：Docker Compose 即开即用，便于本地与服务器快速落地。

## 功能概览
- 数据集上传、解析、建表与预览
- 任务编排与执行（分析、澄清、规划、执行、叙述）
- SQL 生成与执行（sqlite / ClickHouse）
- 图表规划与渲染（ECharts）
- 任务历史与结果回溯
- 数据导出（CSV / 报告）
- 治理策略（最小分组、扫描阈值、限流、导出控制）

## 技术栈
- 后端：FastAPI、Pydantic Settings、SQLAlchemy、Uvicorn
- 前端：React、Vite、Tailwind、ECharts
- 数据：sqlite（默认）、ClickHouse（可选）
- 工程：Docker、Docker Compose

## 架构
- `apps/api`：FastAPI 后端，包含编排状态机、语义层、治理、工具适配器。
- `apps/web`：React 前端，包含对话、任务详情与元数据浏览。
- `packages/contracts`：前后端共享 DTO 与卡片协议。
- `infra`：可选部署资产（nginx、k8s 占位）。

## 数据流概览
用户上传数据集 → 数据落盘与建表 → 语义解析与任务编排 → SQL/Python 执行 → 结果可视化与叙述 → 任务留存与导出。

## 本地开发（非 Docker）
1. 确保 Python 3.11+ 与 Node 18+ 可用。
2. 准备环境变量：
   - `cp .env.example .env`
   - 设置 `LLM_API_KEY` 或 `DASHSCOPE_API_KEY`
   - 如果只用本地 sqlite，保持 `SQL_ENGINE=sqlite`（默认）
3. 启动后端：
   - `pip install -r apps/api/requirements.txt`
   - `cd apps/api/src && uvicorn main:app --reload --host 0.0.0.0 --port 8000`
   - 如果 `.env` 中 `API_PORT` 不是 8000，请将 `--port` 改为一致的端口
4. 启动前端：
   - `corepack enable`
   - `pnpm -C apps/web install`
   - `pnpm -C apps/web dev --host 0.0.0.0`
   - 前端端口由 `VITE_WEB_PORT` 控制（默认 5173）

## Docker 开发（推荐）
1. 准备环境变量：
   - `cp .env.example .env`
   - 设置 `VITE_API_BASE_URL`、`CORS_ORIGINS`、`LLM_API_KEY`/`DASHSCOPE_API_KEY`
2. 启动（包含 ClickHouse）：
   - `docker compose up -d --build`
3. 可选启动 Postgres/Redis（基础设施 profile）：
   - `docker compose --profile infra up -d --build`
4. 查看日志：
   - `docker compose logs -f api`
   - `docker compose logs -f web`

> 如果只用 sqlite：在 `.env` 中设置 `SQL_ENGINE=sqlite`，可以不启动 `clickhouse`。

## 部署（服务器）
### 方案 A：直接 Docker Compose（最省事）
1. 服务器安装 Docker & Compose。
2. 放置代码并创建 `.env`（建议从 `.env.production` 复制）：
   - `APP_ENV=production`
   - `API_PORT=你的后端端口`
   - `VITE_API_BASE_URL=http://你的域名或IP:API_PORT`
   - `CORS_ORIGINS=http://你的域名或IP[,可选端口]`
3. 构建并启动：
   - `docker compose up -d --build`
4. 常见检查：
   - `docker compose ps`
   - `docker compose logs -f api`

### 方案 B：Nginx + 前端静态构建
1. 构建前端：
   - `pnpm -C apps/web install`
   - `pnpm -C apps/web build`
2. 将 `apps/web/dist` 部署到 Nginx 的静态目录（如 `/usr/share/nginx/html`）。
3. 使用 `infra/nginx.conf` 作为模板，配置：
   - `location /api/` 反向代理到后端 `http://api:8000/` 或主机端口。
4. 后端可以用 Docker 或 systemd 启动：
   - Docker：`docker compose up -d --build api`
   - systemd：使用 `uvicorn` 启动 `apps/api/src/main.py`。

## 常见问题
- **CORS 报错**：确保 `.env` 中 `CORS_ORIGINS` 包含前端实际访问的域名/端口。
- **API 地址错误**：确保 `VITE_API_BASE_URL` 与后端实际地址一致。
- **端口不一致**：确保前端 `VITE_API_BASE_URL` 与后端 `API_PORT` 一致。

## 后端接口
- `POST /chat` -> 运行编排并返回任务结果
- `GET /tasks` -> 列出最近任务
- `GET /tasks/{id}` -> 获取任务 spec + result
- `POST /tasks/{id}/rerun` -> 复跑上次参数
- `GET /metrics` / `GET /dimensions` / `GET /catalog`
- `GET /health`

## 鉴权与安全
- `AUTH_TOKEN` 为空时不校验；设置后需在请求头携带 `Authorization: Bearer <token>`。
- 生产环境建议开启 `AUTH_TOKEN`，并配置准确的 `CORS_ORIGINS`。
- `ALLOW_DETAIL_EXPORT`、`MIN_GROUP_SIZE`、`RATE_LIMIT_RPS` 等用于风险控制。

## 数据存储
- sqlite 文件默认在 `apps/api/src/data.db`（可通过 `DATABASE_URL` 修改）。
- 上传文件默认存放在 `UPLOADS_DIR`（默认 `./data/uploads`）。

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
