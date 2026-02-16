#!/bin/bash

# 一键启动前后端开发服务器
# 用法: ./dev.sh
# Ctrl+C 同时停止前后端

cleanup() {
  echo ""
  echo "Stopping all dev servers..."
  kill 0
  wait
}

trap cleanup SIGINT SIGTERM

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting back-end (Flask :5000)..."
(cd "$ROOT_DIR/back-end" && uv run python application.py) &

echo "Starting front-end (Nuxt :3000)..."
(cd "$ROOT_DIR/front-end" && yarn dev) &

echo ""
echo "Both servers running. Press Ctrl+C to stop all."
echo ""

wait
