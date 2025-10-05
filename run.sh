#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "Starting local dev (backend + frontend)..."

# Backend: create venv and run uvicorn
if [ ! -d "$ROOT/backend/.venv" ]; then
  python -m venv "$ROOT/backend/.venv"
fi
# shellcheck disable=SC1090
source "$ROOT/backend/.venv/bin/activate"
pip install -r "$ROOT/backend/requirements.txt"

# run backend in background
cd "$ROOT/backend"
export PYTHONUNBUFFERED=1
export PORT=${PORT:-8000}
uvicorn main:app --host 0.0.0.0 --port $PORT &

# Frontend: run vite in dev mode (optional)
cd "$ROOT/frontend"
npm ci
npm run dev
