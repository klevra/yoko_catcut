#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEFAULT_DIR="$HOME/yoko_catcut"

read -r -p "Install path [$DEFAULT_DIR]: " INSTALL_DIR
INSTALL_DIR="${INSTALL_DIR:-$DEFAULT_DIR}"

if ! command -v git >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y git
fi

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  sudo sh /tmp/get-docker.sh
  sudo usermod -aG docker "$USER" || true
fi

if ! docker compose version >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y docker-compose-plugin
fi

mkdir -p "$INSTALL_DIR"
rsync -a --exclude ".git" --exclude "workspace/*" --exclude "models/*" "$SOURCE_DIR/" "$INSTALL_DIR/"
cd "$INSTALL_DIR"

python3 scripts/account_password.py --workspace ./workspace --user default-user --approve
chmod +x start.command stop.command scripts/reset-password.sh

echo "Installed to $INSTALL_DIR"
echo "Log out/in if docker group membership was just added."
echo "Start with: docker compose up --build -d"
