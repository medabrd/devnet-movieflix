#!/usr/bin/env bash
# Zero-touch deployment script for MovieFlix.
# Usage: ./scripts/deploy.sh [local|remote]
set -euo pipefail

MODE="${1:-local}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log() { printf "\033[1;34m[deploy]\033[0m %s\n" "$*"; }
die() { printf "\033[1;31m[error]\033[0m %s\n" "$*" >&2; exit 1; }

[[ -f "${PROJECT_ROOT}/.env" ]] || die ".env file is missing. Copy .env.example and fill TMDB_API_KEY."

if [[ "${MODE}" == "local" ]]; then
  log "Local deployment via docker compose"
  command -v docker >/dev/null || die "Docker is not installed"
  cd "${PROJECT_ROOT}"
  docker compose pull --ignore-pull-failures || true
  docker compose up -d --build
  log "Waiting for API to become healthy..."
  for i in {1..30}; do
    if curl -fsS "http://localhost:${WEB_PORT:-8080}/api/health" >/dev/null 2>&1; then
      log "API is healthy. UI: http://localhost:${WEB_PORT:-8080}"
      exit 0
    fi
    sleep 2
  done
  die "API did not become healthy in time"

elif [[ "${MODE}" == "remote" ]]; then
  log "Remote deployment via Ansible"
  command -v ansible-playbook >/dev/null || die "ansible-playbook is required"
  cd "${PROJECT_ROOT}/ansible"
  ansible-playbook -i inventory.ini deploy.yml
else
  die "Unknown mode: ${MODE} (use 'local' or 'remote')"
fi
