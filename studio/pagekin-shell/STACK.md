# 本地栈说明

四个服务跑在同一个 compose 里（`docker-compose.yml`）。

| 服务 | 容器名 | 端口 | 数据卷 | 作用 |
|---|---|---|---|---|
| pagekin | pagekin-web | 5180 | `./data/pagekin` | 小说工作台（Electron 主进程 + 浏览器前端） |
| hermes | hermes | 8642 / 9119 | `./data/hermes` | Agent 网关（模型、会话、技能、工具） |
| postgres | novel-pg | 5433 → 5432 | `./data/postgres` | 权威数据库，带 `vector` / `pg_trgm` |
| hindsight | hindsight | 8888 / 9999 | `./data/hindsight` | 记忆层（retain / recall / reflect） |

宿主机端口刻意错开：PG 用 5433，避免与本机已有的 5432 冲突。

## 启动

```bash
cd studio/bases/pagekin
cp .env.example .env        # 填模型密钥
docker compose up -d
docker compose ps
```

按需单独起：

```bash
docker compose up -d postgres pagekin     # 只起数据库 + 工作台
docker compose up -d hermes               # 只起 Agent
```

查看日志：

```bash
docker compose logs -f pagekin
docker compose logs -f hermes
```

## 访问

| 地址 | 说明 |
|---|---|
| http://127.0.0.1:5180 | Pagekin 工作台 |
| http://127.0.0.1:8642 | Hermes 网关 API |
| http://127.0.0.1:9119 | Hermes 面板（需 `HERMES_DASHBOARD=1`） |
| http://127.0.0.1:8888 | Hindsight API |
| http://127.0.0.1:9999 | Hindsight 控制台 |
| `psql -h 127.0.0.1 -p 5433 -U novel` | PostgreSQL |

## Pagekin 的 Web 化：外部加壳，零源码改动

Pagekin 是 Electron 应用。这里**不修改它的任何源码**，而是在外部替换 Electron 这一层：

```
web/shims/electron/index.js   Electron 替身：ipcMain / app / BrowserWindow / dialog / safeStorage …（16 个 API）
web/server.cjs                HTTP /rpc 分发 + SSE /events + 静态托管 + HTML 注入桥接脚本
web/bridge.js                 浏览器侧的 window.aiNovelAPI 实现
Dockerfile.web                构建前端 → 替换 node_modules/electron → 起服务
upgrade.sh                    升级与回滚
```

上游源码保持 `git status` 干净，升级时不会产生合并冲突。

### 三个关键接缝

**1. Electron 边界**
构建镜像时把 `node_modules/electron` 整个替换成 shim。主进程代码里 `require('electron')` 拿到的就是这套实现，**299 个 IPC 通道**全部可用，业务代码一行未改。

**2. 启动握手**
Pagekin 有个门禁：前端必须证明"我是被信任的那个渲染器"，否则停在「启动尚未完成」。校验方式是：

```ts
sender.mainFrame.url === rendererUrl   // rendererUrl = file:///app/dist/index.html
```

shim 用与 `electron/main.ts` 相同的方式算出同一个 `file://` 地址，两边天然相等。**不需要改 `main.ts`**。

**3. 前端桥接**
不改 `index.html`，由服务端在返回 HTML 时注入：

```js
html = html.replace('</head>', '<script src="/web-bridge.js"></script></head>')
```

Electron 环境下 `window.aiNovelAPI` 已由 preload 注入，`bridge.js` 检测到后直接返回，所以同一份产物在桌面与 Web 两种形态下都能跑。

### 改代码的节奏

```bash
docker compose restart pagekin          # 只改了 web/ 下的文件（已挂载，即时生效）
docker compose up -d --build pagekin    # 改了 src/ 或 electron/ 下的上游业务代码
```

## 升级与回滚

一条命令完成：拉取上游 → 重建镜像 → 健康检查 → 失败自动回滚。

```bash
./upgrade.sh
```

它做的事：

1. 检查上游源码是否干净（只看已跟踪文件，`web/`、`data/`、`.env` 不参与）
2. 把当前镜像标记为 `pagekin-web:rollback`
3. `git pull --ff-only`，失败即停，不动当前服务
4. `docker compose build pagekin`
5. 启动后轮询两个条件：`/health` 活着 **且** `startup:get-state` 为 `ready`
6. 任一不满足则把 `rollback` 镜像还原并重启，打印失败日志

> 只检查 `/health` 是不够的——HTTP 活着但启动握手失败时，页面会停在「启动尚未完成」，这正是之前踩过的坑。

## 这套壳什么时候需要动

只有两种情况：

| 现象 | 原因 | 处理 |
|---|---|---|
| 报 `xxx is not a function` | 上游用了新的 Electron API | 在 shim 里补一个桩函数 |
| 停在「启动尚未完成」 | 上游改了启动校验 | 按日志补 sender 字段或地址计算 |

判断方式统一：`docker compose logs --tail 50 pagekin`，找失败的 channel 名。

这是按需补桩的偶发成本，不是每次升级都要动。

## 迁移与备份

`studio/bases/pagekin` 是 Pagekin 上游的**独立 git 仓库**（浅克隆），加壳层是它里面的未跟踪文件，两者互不干扰。

换机器或重建时，需要带走的东西只有：

```
web/                     # 加壳层（约 730 行）
Dockerfile.web
docker-compose.yml
upgrade.sh
.env.example
docker/pg-init/*.sql
STACK.md
```

不带走：`data/`（作品与数据库）、`.env`（密钥）、`node_modules/`、`dist*/`。

重建顺序：

```bash
git clone --filter=blob:none --no-checkout --depth 1 \
  https://github.com/EthanYoQ/Pagekin.git pagekin
cd pagekin && git sparse-checkout init --cone \
  && git sparse-checkout set src electron && git checkout master

# 放回加壳层文件后
cp .env.example .env      # 填密钥
docker compose up -d
```

上游若已前进，`sparse-checkout` 仍是 `src` + `electron`，加壳层不受影响。

## 数据布局

```text
studio/bases/pagekin/data/
├── pagekin/          # 作品、配置、SQLite
│   ├── ai-novel-writer-data/
│   └── projects/
├── hermes/           # Hermes 的 /opt/data：config.yaml、sessions、skills、memories
├── postgres/         # PG 数据目录
└── hindsight/        # Hindsight 本地状态
```

删除容器不影响数据；`rm -rf data/` 才会重置一切。

## Hindsight 与 PostgreSQL 的关系

Hindsight 指向外部 PG（`HINDSIGHT_API_DATABASE_URL`），使用独立数据库 `hindsight`，与业务库 `novel` 隔离。

初始化脚本在 `docker/pg-init/`：

- `10-extensions.sql`：装 `vector`、`pg_trgm`
- `20-hindsight-db.sql`：建 `hindsight` 库

这些脚本只在 PG **首次初始化**（空数据目录）时执行。若 PG 卷已存在，需手动补：

```bash
docker exec novel-pg psql -U novel -d novel -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker exec novel-pg psql -U novel -d novel -c "CREATE DATABASE hindsight;"
```

## Hermes 与 Pagekin 的接线

Hermes 提供 **OpenAI 兼容端点**，不需要写适配代码：

```
POST http://hermes:8642/v1/chat/completions
Authorization: Bearer <API_SERVER_KEY>
{"model": "hermes-agent", "messages": [...]}
```

Pagekin 侧已注册模型条目：

| 字段 | 值 |
|---|---|
| provider / protocol | `custom` / `openai` |
| baseUrl | `http://hermes:8642/v1` |
| modelName | `hermes-agent` |
| apiKey | Hermes 的 `API_SERVER_KEY` |

### 必须改的两处 Hermes 配置

**1. 监听地址**（默认只绑 `127.0.0.1`，同网络的 Pagekin 也访问不到）

写在 `data/hermes/.env`：

```
API_SERVER_HOST=0.0.0.0
```

**2. 上游模型**（默认指向 OpenRouter，没有 key 就跑不起来）

```bash
docker exec hermes hermes config set model.default deepseek-flash
docker exec hermes hermes config set model.provider deepseek
docker exec hermes hermes config set model.base_url https://api.deepseek.com/v1
```

> `deepseek-flash` 即 DeepSeek-V4.1-Flash，1M 上下文、393K 输出。

### 配置命令的坑

`hermes config set` 是 `set <key> <value>` 两个位置参数。在 **zsh 里用 `set -- $var` 分词会失败**（zsh 默认不做词分割），整串会被当成一个键名，写出 `default deepseek-flash: ''` 这种脏配置，导致 YAML 解析失败。

出事后的恢复方式：

```bash
docker exec hermes sh -c "ls -lt /opt/data/backups/config/ | head -3"
docker exec hermes sh -c "cp /opt/data/backups/config/config.yaml.good.<时间戳> /opt/data/config.yaml"
```

Hermes 每次启动会备份配置，坏掉时直接覆盖回去，比手修 YAML 可靠。

## 已知限制

- **镜像体积**：Hermes 镜像含 Playwright/Chromium，体积以 GB 计；Hindsight 次之。首次拉取受网络影响较大。
- **Pagekin 是单用户应用**：没有登录与权限，绑在 `127.0.0.1` 使用，不要直接暴露到公网。
- **文件选择不可用**：`dialog` 在容器里返回「取消」，导入本地文件需要先把文件放进 `./data/pagekin`，后续再补上传接口。
- **Hermes 密钥**：通过 `.env` 注入，不写进镜像；不要把 `.env` 提交到版本库。
