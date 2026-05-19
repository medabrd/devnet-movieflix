# Démarre le backend FastAPI en local (sans Docker)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

# Charger .env
$envFile = Join-Path $root ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "[ERREUR] Fichier .env introuvable. Lance d'abord: Copy-Item .env.example .env" -ForegroundColor Red
    exit 1
}
Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]*?)\s*=\s*(.*?)\s*$") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

if ($env:TMDB_API_KEY -eq "your_tmdb_api_key_here" -or -not $env:TMDB_API_KEY) {
    Write-Host "[ATTENTION] TMDB_API_KEY non configurée dans .env" -ForegroundColor Yellow
    Write-Host "  L'app va démarrer mais les appels TMDB échoueront." -ForegroundColor Yellow
}

Set-Location (Join-Path $root "backend")
Write-Host "[backend] http://localhost:8000 — Swagger: http://localhost:8000/docs" -ForegroundColor Green
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
