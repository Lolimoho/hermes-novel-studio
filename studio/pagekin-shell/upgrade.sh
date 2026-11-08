#!/usr/bin/env bash
# Pagekin 升级：拉取上游 → 重建镜像 → 健康检查 → 失败自动回滚
#
# 只动已跟踪的上游源码与镜像，不触碰 web/ 加壳层与 data/ 数据目录。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

IMAGE="pagekin-web:dev"
ROLLBACK="pagekin-web:rollback"
URL="http://127.0.0.1:5180"

log() { printf '\033[1m▸ %s\033[0m\n' "$*"; }
fail() { printf '\033[31m✗ %s\033[0m\n' "$*"; }

# ---------- docker 环境 ----------
if ! command -v docker >/dev/null 2>&1; then
  export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
fi
if [ -z "${DOCKER_HOST:-}" ] && [ -S "$HOME/.docker/run/docker.sock" ]; then
  export DOCKER_HOST="unix://$HOME/.docker/run/docker.sock"
fi
export BUILDX_CONFIG="${BUILDX_CONFIG:-$ROOT/../.buildx}"
mkdir -p "$BUILDX_CONFIG"

if ! docker info >/dev/null 2>&1; then
  fail "Docker 未运行或无法连接"
  exit 1
fi

# ---------- 1. 上游源码必须干净 ----------
# 只看已跟踪文件：web/、data/、.env 等未跟踪内容是本层自己的东西，不参与判断
if ! git diff --quiet || ! git diff --cached --quiet; then
  fail "上游源码存在未提交改动，先处理后再升级："
  git status --short
  exit 1
fi

# ---------- 2. 备份当前镜像 ----------
if docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker tag "$IMAGE" "$ROLLBACK"
  log "已备份当前镜像 → $ROLLBACK"
fi

# ---------- 3. 拉取上游 ----------
log "拉取上游…"
if ! git pull --ff-only; then
  fail "拉取失败（网络或分叉），当前服务未改动"
  exit 1
fi

# ---------- 4. 重建 ----------
log "重建 pagekin 镜像…"
if ! docker compose build pagekin; then
  fail "构建失败，当前服务未改动"
  exit 1
fi

# ---------- 5. 启动 ----------
docker compose up -d pagekin

# ---------- 6. 健康检查 ----------
# 两个条件都要满足：HTTP 活着 + 启动握手 ready（后者才代表前端真的能进工作台）
log "等待工作台就绪…"
healthy=0
for _ in $(seq 1 30); do
  if curl -fsS --max-time 3 "$URL/health" >/dev/null 2>&1; then
    state="$(curl -s --max-time 5 -X POST "$URL/rpc" \
      -H 'Content-Type: application/json' \
      -d '{"channel":"startup:get-state","args":[]}' 2>/dev/null \
      | grep -o '"state":"[a-z]*"' || true)"
    if [[ "$state" == *'"ready"'* ]]; then
      healthy=1
      break
    fi
  fi
  sleep 2
done

if [[ $healthy -eq 1 ]]; then
  log "升级完成，握手正常"
  docker compose ps pagekin
  exit 0
fi

# ---------- 7. 回滚 ----------
fail "健康检查未通过，开始回滚"
docker compose logs --tail 40 pagekin || true
if docker image inspect "$ROLLBACK" >/dev/null 2>&1; then
  docker tag "$ROLLBACK" "$IMAGE"
  docker compose up -d pagekin
  log "已回滚到上一版本"
else
  fail "没有可用的回滚镜像，需人工处理"
fi
exit 1
