#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

USER_ID="${1:-default-user}"
python3 scripts/account_password.py --workspace ./workspace --user "$USER_ID" --approve
