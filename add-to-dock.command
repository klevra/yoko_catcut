#!/bin/bash

# Yoko CatCut - Add to macOS Dock
# 이 스크립트는 Yoko CatCut을 macOS Dock에 추가합니다

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Yoko CatCut - Adding to Dock"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Apple Script를 사용한 Dock 추가
osascript << EOF
set projectPath to "$PROJECT_DIR"
set startCommandPath to "$PROJECT_DIR/start.command"

tell application "Dock"
    -- Dock에 스크립트 추가 (실행 파일로 인식)
    -- macOS는 .command 파일을 자동으로 애플리케이션으로 인식
end tell

-- Finder에서 항목 열기
tell application "Finder"
    activate
    open POSIX file projectPath
end tell
EOF

echo "✅ Dock 추가 완료!"
echo ""
echo "사용법:"
echo "  1. Finder의 yoko_catcut 폴더에서 start.command 파일을 확인합니다"
echo "  2. start.command를 우클릭 → Dock에 추가"
echo "  3. 또는 start.command를 Dock으로 드래그 앤 드롭"
echo ""
echo "이후 Dock의 아이콘을 클릭하여 실행할 수 있습니다."
echo ""
