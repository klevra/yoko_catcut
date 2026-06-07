# RHEL Install Manual

## Requirements

- RHEL/Rocky/Alma/CentOS compatible host
- sudo 권한
- Network access for Docker repo

## Install

```bash
cd /path/to/yoko_catcut
bash install/rhel/install.sh
```

The installer checks and installs:

- `git`
- Docker CE packages
- Docker Compose plugin

The installer asks for:

- install path, default `~/yoko_catcut`
- default-user password

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
