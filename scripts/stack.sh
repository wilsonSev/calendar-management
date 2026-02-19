#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
LOG_DIR="${ROOT_DIR}/.logs"
GOCACHE_DIR="${GOCACHE:-/tmp/go-cache}"

GATEWAY_PID_FILE="${RUN_DIR}/gateway.pid"
BOT_PID_FILE="${RUN_DIR}/bot.pid"
GATEWAY_LOG_FILE="${LOG_DIR}/gateway.log"
BOT_LOG_FILE="${LOG_DIR}/bot.log"

mkdir -p "${RUN_DIR}" "${LOG_DIR}"

ensure_file() {
  local target="$1"
  local template="$2"

  if [[ -f "${target}" ]]; then
    return
  fi

  cp "${template}" "${target}"
  echo "Created ${target} from ${template}."
}

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Required command not found: ${cmd}" >&2
    exit 1
  fi
}

is_pid_running() {
  local pid="$1"
  kill -0 "${pid}" >/dev/null 2>&1
}

read_pid() {
  local pid_file="$1"
  if [[ ! -f "${pid_file}" ]]; then
    return 1
  fi

  local pid
  pid="$(cat "${pid_file}")"
  if [[ -z "${pid}" ]]; then
    return 1
  fi

  if is_pid_running "${pid}"; then
    echo "${pid}"
    return 0
  fi

  rm -f "${pid_file}"
  return 1
}

start_gateway() {
  if pid="$(read_pid "${GATEWAY_PID_FILE}")"; then
    echo "gateway already running (pid ${pid})"
    return
  fi

  echo "starting gateway..."
  (
    cd "${ROOT_DIR}"
    ENV_FILE=.env GOCACHE="${GOCACHE_DIR}" go run ./services/gateway/cmd/server/main.go
  ) >>"${GATEWAY_LOG_FILE}" 2>&1 &
  echo $! >"${GATEWAY_PID_FILE}"
}

start_bot() {
  if pid="$(read_pid "${BOT_PID_FILE}")"; then
    echo "bot already running (pid ${pid})"
    return
  fi

  echo "starting bot..."
  (
    cd "${ROOT_DIR}"
    ENV_FILE=services/bot/.env GOCACHE="${GOCACHE_DIR}" go run ./services/bot/cmd/bot/main.go
  ) >>"${BOT_LOG_FILE}" 2>&1 &
  echo $! >"${BOT_PID_FILE}"
}

stop_service() {
  local name="$1"
  local pid_file="$2"

  if ! pid="$(read_pid "${pid_file}")"; then
    echo "${name} already stopped"
    rm -f "${pid_file}"
    return
  fi

  echo "stopping ${name} (pid ${pid})..."
  kill "${pid}" >/dev/null 2>&1 || true

  for _ in $(seq 1 20); do
    if ! is_pid_running "${pid}"; then
      rm -f "${pid_file}"
      echo "${name} stopped"
      return
    fi
    sleep 0.25
  done

  echo "forcing ${name} stop..."
  kill -9 "${pid}" >/dev/null 2>&1 || true
  rm -f "${pid_file}"
}

status_service() {
  local name="$1"
  local pid_file="$2"
  local log_file="$3"

  if pid="$(read_pid "${pid_file}")"; then
    echo "${name}: running (pid ${pid})"
  else
    echo "${name}: stopped"
  fi
  echo "${name} log: ${log_file}"
}

run_migrations() {
  echo "running migrations..."
  (
    cd "${ROOT_DIR}"
    ENV_FILE=.env GOCACHE="${GOCACHE_DIR}" go run ./services/gateway/cmd/migrate
  )
}

usage() {
  cat <<EOF
Usage: scripts/stack.sh <start|stop|restart|status|logs>

Commands:
  start   Run migrations, then start gateway + bot in background
  stop    Stop bot + gateway
  restart Stop and start both services
  status  Show service states and log file locations
  logs    Tail both logs
EOF
}

main() {
  require_cmd go
  ensure_file "${ROOT_DIR}/.env" "${ROOT_DIR}/.env.example"
  ensure_file "${ROOT_DIR}/services/bot/.env" "${ROOT_DIR}/services/bot/.env.example"

  local command="${1:-}"
  case "${command}" in
    start)
      run_migrations
      start_gateway
      sleep 1
      start_bot
      status_service "gateway" "${GATEWAY_PID_FILE}" "${GATEWAY_LOG_FILE}"
      status_service "bot" "${BOT_PID_FILE}" "${BOT_LOG_FILE}"
      ;;
    stop)
      stop_service "bot" "${BOT_PID_FILE}"
      stop_service "gateway" "${GATEWAY_PID_FILE}"
      ;;
    restart)
      stop_service "bot" "${BOT_PID_FILE}"
      stop_service "gateway" "${GATEWAY_PID_FILE}"
      run_migrations
      start_gateway
      sleep 1
      start_bot
      status_service "gateway" "${GATEWAY_PID_FILE}" "${GATEWAY_LOG_FILE}"
      status_service "bot" "${BOT_PID_FILE}" "${BOT_LOG_FILE}"
      ;;
    status)
      status_service "gateway" "${GATEWAY_PID_FILE}" "${GATEWAY_LOG_FILE}"
      status_service "bot" "${BOT_PID_FILE}" "${BOT_LOG_FILE}"
      ;;
    logs)
      touch "${GATEWAY_LOG_FILE}" "${BOT_LOG_FILE}"
      tail -n 100 -f "${GATEWAY_LOG_FILE}" "${BOT_LOG_FILE}"
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"

