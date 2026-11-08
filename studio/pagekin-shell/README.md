# pagekin-shell

Pagekin 的 **Web 加壳层**。让 Electron 桌面应用以 Web 形式运行，并把模型接到 Hermes。

这里只放我们自己写的代码。Pagekin 上游是独立仓库，不进本仓库。

## 为什么单独放

Pagekin 是第三方项目（GPL-3.0），由它自己的 git 仓库维护。我们只加一层壳，不改它的源码。

如果壳放在上游目录里，会跟着一起被忽略；放在这里，既能版本控制，又能在上游升级时保持零冲突。

## 结构

```text
pagekin-shell/
├── web/
│   ├── shims/electron/index.js   Electron 替身（ipcMain / app / BrowserWindow / dialog / safeStorage …）
│   ├── shims/electron/package.json
│   ├── server.cjs                HTTP /rpc + SSE /events + 静态托管 + HTML 注入
│   └── bridge.js                 浏览器侧 window.aiNovelAPI
├── Dockerfile.web                构建前端 → 替换 node_modules/electron → 起服务
├── docker-compose.yml            pagekin + hermes + postgres + hindsight
├── docker/pg-init/               PG 初始化（vector / pg_trgm / hindsight 库）
├── upgrade.sh                    升级与回滚
├── apply.sh                      把本目录同步到 Pagekin 工作副本
├── .env.example                  密钥模板
├── .dockerignore
└── STACK.md                      部署与运维说明
```

## 三个接缝

| 接缝 | 做法 |
|---|---|
| Electron 边界 | 构建时把 `node_modules/electron` 换成 shim，299 个 IPC 通道照常 |
| 启动握手 | shim 按上游同样的方式算出 `file:///app/dist/index.html`，与 `rendererUrl` 天然相等 |
| 前端桥接 | 服务端返回 HTML 时注入 `<script src="/web-bridge.js">`，不改 `index.html` |

Pagekin 源码 **零改动**：`git status` 在它的仓库里是干净的。

## 部署

```bash
# 1. 取上游（只取需要的目录，约 20MB）
cd studio/bases
git clone --filter=blob:none --no-checkout --depth 1 \
  https://github.com/EthanYoQ/Pagekin.git pagekin
cd pagekin
git sparse-checkout init --cone
git sparse-checkout set src electron
git checkout master

# 2. 铺加壳层
cd ../../pagekin-shell
./apply.sh

# 3. 配置并启动
cd ../bases/pagekin
cp /path/to/pagekin-shell/.env.example .env   # 填密钥
docker compose up -d
```

## 升级

```bash
cd studio/bases/pagekin
./upgrade.sh
```

流程：检查源码干净 → 备份当前镜像 → `git pull --ff-only` → 重建 → 健康检查 → 失败自动回滚。

健康检查看两个条件：`/health` 活着 **且** `startup:get-state` 为 `ready`。只看前者会漏掉「HTTP 正常但页面卡在启动」的情况。

## 敏感面

上游变化时，只有两种情况需要动这层壳：

| 现象 | 处理 |
|---|---|
| `xxx is not a function` | 在 shim 里补桩函数 |
| 停在「启动尚未完成」 | 按日志补 sender 字段或地址计算 |

其余（UI、数据库、写作流程、Hermes 接入）都不受影响。

## 模型接入

Hermes 提供 OpenAI 兼容端点，Pagekin 用 `provider: custom` 直接接，**零代码**：

```
baseUrl: http://hermes:8642/v1
model:   hermes-agent
apiKey:  API_SERVER_KEY
```

配置细节见 `STACK.md`。

## 许可

本目录代码为本项目自有。Pagekin 上游为 GPL-3.0，Hermes 与 Hindsight 各自遵循其许可。仅自用部署，不对外分发。
