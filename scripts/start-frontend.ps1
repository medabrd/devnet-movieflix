# Démarre le frontend React (Vite dev server)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "frontend")
Write-Host "[frontend] http://localhost:5173" -ForegroundColor Green
npm run dev
