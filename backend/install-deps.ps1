# Upgrades pip then installs requirements (fixes TomlError with old pip 19.x)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating venv..."
    python -m venv .venv
}
& .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
& .\.venv\Scripts\pip.exe install -r requirements.txt
Write-Host "Done. Activate: .\.venv\Scripts\Activate.ps1"
