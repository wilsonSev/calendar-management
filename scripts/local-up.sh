#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

ensure_file() {
  local target="$1"
  local template="$2"

  if [[ -f "${target}" ]]; then
    return
  fi

  cp "${template}" "${target}"
  echo "Created ${target} from ${template}. Fill in required values before production use."
}

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Required command not found: ${cmd}" >&2
    exit 1
  fi
}

require_cmd docker
require_cmd go

if ! docker info >/dev/null 2>&1; then
  echo "Docker daemon is not running. Start Docker and rerun scripts/local-up.sh" >&2
  exit 1
fi

ensure_file ".env" ".env.example"
ensure_file "services/bot/.env" "services/bot/.env.example"

echo "Starting postgres..."
docker compose up -d postgres

echo "Waiting for postgres readiness..."
for i in $(seq 1 60); do
  if docker compose exec -T postgres pg_isready >/dev/null 2>&1; then
    break
  fi

  if [[ "${i}" == "60" ]]; then
    echo "Postgres did not become ready in time" >&2
    exit 1
  fi

  sleep 1
done

echo "Applying migrations..."
ENV_FILE=.env GOCACHE="${GOCACHE:-/tmp/go-cache}" go run ./services/gateway/cmd/migrate

echo "Starting gateway and bot. Press Ctrl+C to stop."
ENV_FILE=.env GOCACHE="${GOCACHE:-/tmp/go-cache}" go run ./services/gateway/cmd/server/main.go &
gateway_pid=$!
ENV_FILE=services/bot/.env GOCACHE="${GOCACHE:-/tmp/go-cache}" go run ./services/bot/cmd/bot/main.go &
bot_pid=$!

cleanup() {
  kill "${gateway_pid}" "${bot_pid}" 2>/dev/null || true
  wait "${gateway_pid}" "${bot_pid}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

wait -n "${gateway_pid}" "${bot_pid}"
