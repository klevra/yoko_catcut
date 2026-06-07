# macOS Install Manual

## Requirements

- macOS 10.15+
- Git
- Docker Desktop
- Python 3

## Install

```bash
cd /path/to/yoko_catcut
bash install/macos/install.sh
```

The installer asks for:

- install path, default `~/Applications/yoko_catcut`
- default-user password

If Docker Desktop is missing and Homebrew is available, the installer runs:

```bash
brew install --cask docker
```

## Start

```bash
~/Applications/yoko_catcut/start.command
```

## Reset Password

```bash
cd ~/Applications/yoko_catcut
scripts/reset-password.sh default-user
```
