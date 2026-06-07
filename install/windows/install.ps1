param(
  [string]$InstallDir = "$env:USERPROFILE\yoko_catcut"
)

$ErrorActionPreference = "Stop"
$SourceDir = Resolve-Path (Join-Path $PSScriptRoot "..\..")

function Ensure-Command($Name, $InstallCommand) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    Write-Host "$Name not found. Running: $InstallCommand"
    Invoke-Expression $InstallCommand
  }
}

Ensure-Command "git" "winget install --id Git.Git -e"
Ensure-Command "docker" "winget install --id Docker.DockerDesktop -e"
Ensure-Command "py" "winget install --id Python.Python.3.11 -e"

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
robocopy $SourceDir $InstallDir /E /XD .git workspace models node_modules dist | Out-Null
Set-Location $InstallDir

py -3 scripts/account_password.py --workspace ./workspace --user default-user --approve

Write-Host "Installed to $InstallDir"
Write-Host "Start with: docker compose up --build -d"
