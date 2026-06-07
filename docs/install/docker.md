# Docker Image Install Manual

## Requirements

- Docker
- Docker Compose plugin
- Python 3 for default password setup

## Install

```bash
cd /path/to/yoko_catcut
bash install/docker/install.sh
```

The installer asks for the default-user password and runs:

```bash
docker compose build
```

## Start

```bash
docker compose up -d
```

## Reset Password

```bash
scripts/reset-password.sh default-user
```
