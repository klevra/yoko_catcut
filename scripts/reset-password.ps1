param(
  [string]$UserId = "default-user"
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectDir

py -3 scripts/account_password.py --workspace ./workspace --user $UserId --approve
