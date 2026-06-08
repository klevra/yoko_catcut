# Windows Install Manual

## Requirements

- Windows 10+
- PowerShell
- winget
- Docker Desktop with WSL2 backend

## Install

Open PowerShell:

```powershell
cd C:\path\to\yoko_catcut
powershell -ExecutionPolicy Bypass -File install\windows\install.ps1
```

Install directly from GitHub without cloning first:

```powershell
Invoke-WebRequest `
  -Uri https://raw.githubusercontent.com/klevra/yoko_catcut/main/install/windows/install.ps1 `
  -OutFile install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1 -DownloadFromGit
```

Optional install path:

```powershell
powershell -ExecutionPolicy Bypass -File install\windows\install.ps1 -InstallDir D:\Apps\yoko_catcut
```

The installer checks and installs with winget:

- Docker Desktop
- Python 3.11

When `-DownloadFromGit` is used, the installer downloads the latest source ZIP from:

```text
https://github.com/klevra/yoko_catcut/archive/refs/heads/main.zip
```

By default, service dependencies are installed by Docker image builds:

- Backend image installs OS packages: ffmpeg, fontconfig, fonts-noto-cjk
- Backend image installs Python libraries from `backend/requirements.txt`
- Frontend image installs Node libraries from `frontend/package.json`

For local development without relying only on Docker images, run:

```powershell
powershell -ExecutionPolicy Bypass -File install\windows\install.ps1 -InstallNativeDependencies
```

This additionally checks or installs:

- FFmpeg
- Node.js LTS and npm
- Backend Python virtual environment at `backend\.venv`
- Python libraries from `backend\requirements.txt`
- Frontend libraries with `npm install`

The installer asks for the default-user password.

## Start

```powershell
cd $env:USERPROFILE\yoko_catcut
docker compose up --build -d
```

## Reset Password

```powershell
cd $env:USERPROFILE\yoko_catcut
powershell -ExecutionPolicy Bypass -File scripts\reset-password.ps1 default-user
```
