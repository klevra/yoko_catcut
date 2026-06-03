#!/bin/bash

# Yoko CatCut Startup Script
# macOS GUI 더블클릭으로 실행 가능

set -e

# 프로젝트 디렉토리
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Yoko CatCut - Starting Application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Docker 실행 중인지 확인
if docker ps -a | grep -q "yoko_catcut_backend"; then
    echo "ℹ️  이전 컨테이너 발견. 중지 중..."
    docker compose down 2>/dev/null || true
    sleep 2
fi

echo "▶️  Docker Compose 시작 중..."
docker compose up --build -d

# 서버 준비 대기
echo "⏳ 백엔드 서버 준비 중..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ 백엔드 서버 준비 완료!"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "⏳ 프론트엔드 서버 준비 중..."
sleep 3

# 브라우저 자동 실행
echo "🌐 브라우저 실행 중..."
if command -v open &> /dev/null; then
    # macOS
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:3000 &
elif command -v start &> /dev/null; then
    # Windows
    start http://localhost:3000
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Yoko CatCut 실행 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 Frontend:  http://localhost:3000"
echo "🔗 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "중지하려면 stop.command를 실행하세요."
echo ""
