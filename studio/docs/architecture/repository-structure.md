# Studio 仓库结构规划

状态：M0 规划基线，具体目录在对应里程碑启动时创建。

## 目标结构

```text
studio/
├── README.md
├── AGENTS.md
├── apps/
│   └── novel-ui/                    # React + TypeScript 小说工作区
├── services/
│   └── novel-api/                   # FastAPI 领域服务与后台任务
│       ├── app/
│       │   ├── api/                 # HTTP/SSE API
│       │   ├── domain/              # 领域模型与业务规则
│       │   ├── application/         # 用例、事务和工作流
│       │   ├── infrastructure/      # Postgres/Hermes/Hindsight适配
│       │   └── workers/             # Outbox与自动创作任务
│       ├── migrations/              # Alembic迁移
│       └── tests/
├── packages/
│   ├── shared-contracts/            # OpenAPI生成类型与共享协议
│   ├── novel-ui-core/               # 与宿主无关的领域UI组件
│   └── hermes-adapter/              # Desktop SDK与HTTP适配接口
├── plugins/
│   └── hermes-novel-studio/
│       ├── plugin.yaml              # Hermes Agent插件清单
│       ├── skills/                  # Studio专用薄Skill/工具说明
│       ├── dashboard/
│       │   └── plugin_api.py        # 轻量Hermes桥接路由
│       └── desktop/
│           └── plugin.js            # Hermes Desktop入口与宿主适配
├── docs/
│   ├── product/                     # 产品范围、术语、用户流程
│   ├── architecture/                # 系统、数据、安全和集成设计
│   ├── api/                         # API约定与事件协议
│   ├── decisions/                   # ADR架构决策
│   └── project-management/          # 里程碑、状态、验收和变更控制
├── tests/
│   ├── e2e/                         # 跨UI/API/Agent关键路径
│   ├── contract/                    # Hermes/Hindsight契约测试
│   └── fixtures/                    # 隔离的示例小说与测试数据
├── infra/
│   ├── compose/                     # 本地Postgres/Hindsight编排
│   └── deployment/                  # 后续部署配置
└── scripts/                         # 开发、验证、迁移和发布入口
```

## 目录创建原则

- M0只维护 `docs/` 与项目治理文件。
- M1创建工程骨架、`services/`、`apps/`、迁移和基础测试。
- M3开始创建 Hermes 领域适配。
- M4创建正式 Desktop 插件交付结构。
- M5以后接入 Kanban、Hindsight和自动化，不提前放置空实现。

## 依赖方向

```text
novel-ui / desktop-plugin
            ↓
      shared-contracts
            ↓
         novel-api
       ↙     ↓      ↘
PostgreSQL  Hermes  Hindsight
```

- UI不直接访问PostgreSQL。
- UI不持有模型提供商密钥。
- Hermes插件后端保持轻量，核心领域逻辑只存在于 `novel-api`。
- `novel-api` 不读取Hindsight内部表，只调用公开接口。
- `skill/` 通过受控适配被 Studio 使用，不作为Studio运行状态存储。

