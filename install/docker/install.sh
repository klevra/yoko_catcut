#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for docker image installation."
  exit 1
fi

python3 scripts/account_password.py --workspace ./workspace --user default-user --approve
docker compose build

echo "Docker images built."
echo "Start with: docker compose up -d"
