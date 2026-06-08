param(
  [string]$InstallDir = "$env:USERPROFILE\yoko_catcut",
  [string]$ArchiveUrl = "https://github.com/klevra/yoko_catcut/archive/refs/heads/main.zip",
  [switch]$DownloadFromGit,
  [switch]$InstallNativeDependencies,
  [switch]$SkipDockerBuild
)

$ErrorActionPreference = "Stop"

function Ensure-Command($Name, $InstallCommand) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    Write-Host "$Name not found. Running: $InstallCommand"
    Invoke-Expression $InstallCommand
  }
}

function Get-SourceDir {
  if ($DownloadFromGit) {
    Ensure-Command "curl.exe" "winget install --id cURL.cURL -e"

    $TempDir = Join-Path $env:TEMP ("yoko_catcut_install_" + [guid]::NewGuid().ToString())
    $ZipPath = Join-Path $TempDir "source.zip"
    New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

    Write-Host "Downloading source: $ArchiveUrl"
    curl.exe -L $ArchiveUrl -o $ZipPath

    Write-Host "Extracting source..."
    Expand-Archive -Path $ZipPath -DestinationPath $TempDir -Force
    $ExtractedDir = Get-ChildItem -Path $TempDir -Directory | Select-Object -First 1
    if (-not $ExtractedDir) {
      throw "No extracted source directory found."
    }
    $ExtractedPath = $ExtractedDir.FullName
    return Resolve-Path -Path $ExtractedPath
  }

  return Resolve-Path (Join-Path $PSScriptRoot "..\..")
}

Ensure-Command "docker" "winget install --id Docker.DockerDesktop -e"
Ensure-Command "py" "winget install --id Python.Python.3.11 -e"

$SourceDir = Get-SourceDir

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$RoboCopyExitCode = 0
robocopy $SourceDir $InstallDir /E /XD .git workspace models node_modules dist .venv | Out-Null
$RoboCopyExitCode = $LASTEXITCODE
if ($RoboCopyExitCode -ge 8) {
  throw "robocopy failed with exit code $RoboCopyExitCode"
}

Set-Location $InstallDir

py -3 scripts/account_password.py --workspace ./workspace --user default-user --approve

if ($InstallNativeDependencies) {
  Ensure-Command "ffmpeg" "winget install --id Gyan.FFmpeg -e"
  Ensure-Command "node" "winget install --id OpenJS.NodeJS.LTS -e"
  Ensure-Command "npm" "winget install --id OpenJS.NodeJS.LTS -e"

  Write-Host "Installing backend Python libraries from backend\requirements.txt"
  py -3 -m venv backend\.venv
  .\backend\.venv\Scripts\python.exe -m pip install --upgrade pip
  .\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

  Write-Host "Installing frontend Node libraries from frontend\package.json"
  Push-Location frontend
  npm install
  Pop-Location
}

if (-not $SkipDockerBuild) {
  Write-Host "Building Docker images and installing service dependencies"
  docker compose build
}

Write-Host "Installed to $InstallDir"
Write-Host "Start with: docker compose up --build -d"
