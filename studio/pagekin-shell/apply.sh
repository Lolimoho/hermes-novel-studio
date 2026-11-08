#!/usr/bin/env bash
# 把加壳层同步到 Pagekin 工作副本
#
# 用法：
#   ./apply.sh                       # 同步到默认位置 ../bases/pagekin
#   ./apply.sh /path/to/pagekin      # 同步到指定目录
set -euo pipefail

SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$SHELL_DIR/../bases/pagekin}"

if [ ! -d "$TARGET/electron" ] || [ ! -f "$TARGET/package.json" ]; then
  echo "✗ 目标不是 Pagekin 目录：$TARGET"
  exit 1
fi

echo "▸ 同步加壳层 → $TARGET"

# 逐项覆盖，不做整目录删除，避免误删上游文件
for item in web docker; do
  mkdir -p "$TARGET/$item"
  cp -R "$SHELL_DIR/$item/." "$TARGET/$item/"
done

for f in Dockerfile.web docker-compose.yml upgrade.sh .env.example .dockerignore STACK.md; do
  cp -f "$SHELL_DIR/$f" "$TARGET/$f"
done

chmod +x "$TARGET/upgrade.sh"

echo "✓ 完成。下一步："
echo "    cd $TARGET && docker compose up -d"
