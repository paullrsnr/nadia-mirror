Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "🚀 Build backend Windows" -ForegroundColor Cyan

Set-Location backend

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

pyinstaller nadia-backend.spec

New-Item -ItemType Directory -Force dist\win | Out-Null
Move-Item dist\nadia-backend.exe dist\win\nadia-backend.exe -Force

Write-Host "✅ Backend Windows build terminé" -ForegroundColor Green