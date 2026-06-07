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

Optional install path:

```powershell
powershell -ExecutionPolicy Bypass -File install\windows\install.ps1 -InstallDir D:\Apps\yoko_catcut
```

The installer checks and installs with winget:

- Git
- Docker Desktop
- Python 3.11

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
