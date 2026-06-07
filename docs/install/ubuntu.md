# Ubuntu Install Manual

## Requirements

- Ubuntu 20.04+
- sudo 권한
- Network access for Docker install

## Install

```bash
cd /path/to/yoko_catcut
bash install/ubuntu/install.sh
```

The installer checks and installs:

- `git`
- Docker Engine
- Docker Compose plugin

The installer asks for:

- install path, default `~/yoko_catcut`
- default-user password

If Docker group membership is added, log out and back in before starting.

## Start

```bash
cd ~/yoko_catcut
docker compose up --build -d
```

## Reset Password

```bash
cd ~/yoko_catcut
scripts/reset-password.sh default-user
```
