#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEFAULT_DIR="$HOME/Applications/yoko_catcut"

read -r -p "Install path [$DEFAULT_DIR]: " INSTALL_DIR
INSTALL_DIR="${INSTALL_DIR:-$DEFAULT_DIR}"

if ! command -v git >/dev/null 2>&1; then
  echo "git not found. Install Xcode Command Line Tools: xcode-select --install"
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    echo "Installing Docker Desktop with Homebrew..."
    brew install --cask docker
  else
    echo "Docker not found. Install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
  fi
fi

mkdir -p "$INSTALL_DIR"
rsync -a --exclude ".git" --exclude "workspace/*" --exclude "models/*" "$SOURCE_DIR/" "$INSTALL_DIR/"
cd "$INSTALL_DIR"

python3 scripts/account_password.py --workspace ./workspace --user default-user --approve
chmod +x start.command stop.command scripts/reset-password.sh

echo "Installed to $INSTALL_DIR"
echo "Start with: $INSTALL_DIR/start.command"
