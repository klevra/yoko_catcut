
#!/bin/bash

# Yoko CatCut Startup Script
# macOS GUI 더블클릭으로 실행 가능

set -e

# 프로젝트 디렉토리
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# macOS GUI에서 실행될 때 PATH가 제한될 수 있으므로 명시적으로 설정
if [ -f "$HOME/.zprofile" ]; then
    source "$HOME/.zprofile"
fi
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
export HISTFILE=/dev/null

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Yoko CatCut - Starting Application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Docker CLI 확인
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

# application.yml 생성 (템플릿에서 환경변수 치환)
if [ -f "$PROJECT_DIR/application.yml.template" ]; then
    echo "▶️  Generating application.yml from template..."
    if command -v envsubst >/dev/null 2>&1; then
        envsubst < "$PROJECT_DIR/application.yml.template" > "$PROJECT_DIR/application.yml"
    else
        perl -pe 's/\$\{([^}\:]+)(?:[^}]*)?\}/(defined $ENV{$1} ? $ENV{$1} : "")/ge' "$PROJECT_DIR/application.yml.template" > "$PROJECT_DIR/application.yml"
    fi
fi

# Docker 실행 중인지 확인 및 정리
BACKEND_NAME="${BACKEND_CONTAINER_NAME:-yoko_catcut_backend}"
if docker ps -a | grep -q "$BACKEND_NAME"; then
    echo "ℹ️  이전 컨테이너 발견. 중지 중..."
    docker compose down 2>/dev/null || true
    sleep 2
fi

echo "▶️  Docker Compose 시작 중..."
docker compose up --build -d

# 서버 준비 대기 (호스트 포트 사용)
BACKEND_HOST_PORT="${BACKEND_HOST_PORT:-8000}"
FRONTEND_HOST_PORT="${FRONTEND_HOST_PORT:-3000}"

echo "⏳ 백엔드 서버 준비 중..."
for i in {1..30}; do
    if curl -s http://localhost:${BACKEND_HOST_PORT}/api/v1/health > /dev/null 2>&1; then
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
    open "http://localhost:${FRONTEND_HOST_PORT}"
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:${FRONTEND_HOST_PORT}" &
elif command -v start &> /dev/null; then
    start "http://localhost:${FRONTEND_HOST_PORT}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Yoko CatCut 실행 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 Frontend:  http://localhost:${FRONTEND_HOST_PORT}"
echo "🔗 Backend:   http://localhost:${BACKEND_HOST_PORT}"
echo "📚 API Docs:  http://localhost:${BACKEND_HOST_PORT}/docs"
echo ""
echo "중지하려면 stop.command를 실행하세요."
echo ""

