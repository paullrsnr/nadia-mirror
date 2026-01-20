Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "📦 Packaging Electron Windows" -ForegroundColor Cyan

Set-Location desktop

npm install
npm run build

# requis par electron-builder
New-Item -ItemType Directory -Force ..\backend\dist\mac | Out-Null

npm run pack:win

Write-Host "✅ Packaging Windows terminé" -ForegroundColor Green