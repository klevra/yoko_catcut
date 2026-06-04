#!/bin/bash

# Yoko CatCut Shutdown Script
# macOS GUI 더블클릭으로 실행 가능

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# macOS GUI에서 실행될 때 PATH가 제한될 수 있으므로 명시적으로 설정
if [ -f "$HOME/.zprofile" ]; then
    source "$HOME/.zprofile"
fi
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
export HISTFILE=/dev/null

if ! command -v docker >/dev/null 2>&1; then
    echo "🚨 docker CLI를 찾을 수 없습니다. Docker Desktop을 설치하고 다시 시도하세요."
    exit 1
fi

# .env 또는 .env.example 로드
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
elif [ -f "$PROJECT_DIR/.env.example" ]; then
    set -a
    source "$PROJECT_DIR/.env.example"
    set +a
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Yoko CatCut - Stopping Application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Docker Compose 중지
echo "⏹️  Docker Compose 중지 중..."
docker compose down || true

echo ""

# 환경 변수 기반 컨테이너 이름으로 남아있는 컨테이너 강제 제거
BACKEND_NAME="${BACKEND_CONTAINER_NAME:-yoko_catcut_backend}"
FRONTEND_NAME="${FRONTEND_CONTAINER_NAME:-yoko_catcut_frontend}"

for name in "$BACKEND_NAME" "$FRONTEND_NAME"; do
    if docker ps -a --format '{{.Names}}' | grep -xq "$name"; then
        echo "⏹️  Removing container $name"
        docker rm -f "$name" 2>/dev/null || true
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Yoko CatCut 중지 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 3초 후 자동 종료
sleep 3
