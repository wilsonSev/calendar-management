#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
LOG_DIR="${ROOT_DIR}/.logs"
GOCACHE_DIR="${GOCACHE:-/tmp/go-cache}"

GATEWAY_PID_FILE="${RUN_DIR}/gateway.pid"
BOT_PID_FILE="${RUN_DIR}/bot.pid"
NLP_PID_FILE="${RUN_DIR}/nlp.pid"
ROUTER_PID_FILE="${RUN_DIR}/router.pid"

GATEWAY_LOG_FILE="${LOG_DIR}/gateway.log"
BOT_LOG_FILE="${LOG_DIR}/bot.log"
NLP_LOG_FILE="${LOG_DIR}/nlp.log"
ROUTER_LOG_FILE="${LOG_DIR}/router.log"

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


kill_by_pattern() {
  local pattern="$1"
  # Находим PID процессов, соответствующих паттерну, исключая grep и сам скрипт
  # Используем pgrep для более точного поиска если возможно, или ps
  pids=$(ps -eo pid,command | grep "${pattern}" | grep -v grep | grep -v "$0" | awk '{print $1}' || true)
  
  if [[ -n "${pids}" ]]; then
    echo "Killing lingering processes for '${pattern}': ${pids}"
    echo "${pids}" | xargs kill -9 2>/dev/null || true
  fi
}

start_nlp() {
  kill_by_pattern "nlp/grpc_server.py"
  
  if pid="$(read_pid "${NLP_PID_FILE}")"; then
    echo "nlp already running (pid ${pid})"
    return
  fi

  echo "starting nlp..."
  # Ensure venv exists
  if [ ! -d "${ROOT_DIR}/nlp/venv" ]; then
    echo "Creating virtual environment for NLP..."
    (cd "${ROOT_DIR}" && python3 -m venv nlp/venv)
  fi

  # Helper script to run NLP in background with venv
  cat <<EOF > "${RUN_DIR}/run_nlp_bg.sh"
#!/bin/bash
source "${ROOT_DIR}/nlp/venv/bin/activate"
export PYTHONPATH="${ROOT_DIR}/nlp:\$PYTHONPATH"
export NLP_PORT="50052"
exec python3 "${ROOT_DIR}/nlp/grpc_server.py"
EOF
  chmod +x "${RUN_DIR}/run_nlp_bg.sh"

  "${RUN_DIR}/run_nlp_bg.sh" >>"${NLP_LOG_FILE}" 2>&1 &
  echo $! >"${NLP_PID_FILE}"
}

start_router() {
  kill_by_pattern "router/cmd/router/main.go"

  if pid="$(read_pid "${ROUTER_PID_FILE}")"; then
    echo "router already running (pid ${pid})"
    return
  fi

  echo "starting router..."
  (
    cd "${ROOT_DIR}"
    ENV_FILE=router/config/local.yaml GOCACHE="${GOCACHE_DIR}" go run ./router/cmd/router/main.go
  ) >>"${ROUTER_LOG_FILE}" 2>&1 &
  echo $! >"${ROUTER_PID_FILE}"
}

start_gateway() {
  kill_by_pattern "services/gateway/cmd/server/main.go"
  
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
  kill_by_pattern "services/bot/cmd/bot/main.go"

  if pid="$(read_pid "${BOT_PID_FILE}")"; then
    echo "bot already running (pid ${pid})"
    return
  fi

  echo "starting bot..."
  (
    cd "${ROOT_DIR}"
    ENV_FILE=services/bot/.env ANALYZER_TARGET=localhost:50052 GOCACHE="${GOCACHE_DIR}" go run ./services/bot/cmd/bot/main.go
  ) >>"${BOT_LOG_FILE}" 2>&1 &
  echo $! >"${BOT_PID_FILE}"
}

stop_service() {
  local name="$1"
  local pid_file="$2"
  local pattern="$3"

  if pid="$(read_pid "${pid_file}")"; then
      echo "stopping ${name} (pid ${pid})..."
      kill "${pid}" >/dev/null 2>&1 || true

      for _ in $(seq 1 5); do
        if ! is_pid_running "${pid}"; then
          rm -f "${pid_file}"
          echo "${name} stopped"
          break
        fi
        sleep 0.25
      done
  fi
  
  # Ensure cleanup
  rm -f "${pid_file}"
  kill_by_pattern "${pattern}"
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
    ENV_FILE=.env GOCACHE="${GOCACHE_DIR}" go run ./services/gateway/cmd/migrate/main.go
  )
}

usage() {
  echo "Usage: $0 {start|stop|restart|status|logs}"
}

main() {
  local command="${1:-}"
  case "${command}" in
    start)
      run_migrations
      start_router
      sleep 1
      start_gateway
      sleep 1
      start_bot
      sleep 1
      start_nlp
      status_service "router" "${ROUTER_PID_FILE}" "${ROUTER_LOG_FILE}"
      status_service "gateway" "${GATEWAY_PID_FILE}" "${GATEWAY_LOG_FILE}"
      status_service "bot" "${BOT_PID_FILE}" "${BOT_LOG_FILE}"
      status_service "nlp" "${NLP_PID_FILE}" "${NLP_LOG_FILE}"
      ;;
    stop)
      stop_service "bot" "${BOT_PID_FILE}" "services/bot/cmd/bot/main.go"
      stop_service "gateway" "${GATEWAY_PID_FILE}" "services/gateway/cmd/server/main.go"
      stop_service "nlp" "${NLP_PID_FILE}" "nlp/grpc_server.py"
      stop_service "router" "${ROUTER_PID_FILE}" "router/cmd/router/main.go"
      # Cleanup any orphaned go run or python processes related to the project
      kill_by_pattern "services/bot/cmd/bot/main.go"
      kill_by_pattern "services/gateway/cmd/server/main.go"
      kill_by_pattern "nlp/grpc_server.py"
      kill_by_pattern "router/cmd/router/main.go"
      ;;
    restart)
      stop_service "bot" "${BOT_PID_FILE}" "services/bot/cmd/bot/main.go"
      stop_service "gateway" "${GATEWAY_PID_FILE}" "services/gateway/cmd/server/main.go"
      stop_service "nlp" "${NLP_PID_FILE}" "nlp/grpc_server.py"
      stop_service "router" "${ROUTER_PID_FILE}" "router/cmd/router/main.go"
      # Extra cleanup
      kill_by_pattern "services/bot/cmd/bot/main.go"
      kill_by_pattern "services/gateway/cmd/server/main.go"
      kill_by_pattern "nlp/grpc_server.py"
      kill_by_pattern "router/cmd/router/main.go"
      
      run_migrations
      start_router
      sleep 1
      start_gateway
      sleep 1
      start_bot
      sleep 1
      start_nlp
      status_service "router" "${ROUTER_PID_FILE}" "${ROUTER_LOG_FILE}"
      status_service "gateway" "${GATEWAY_PID_FILE}" "${GATEWAY_LOG_FILE}"
      status_service "bot" "${BOT_PID_FILE}" "${BOT_LOG_FILE}"
      status_service "nlp" "${NLP_PID_FILE}" "${NLP_LOG_FILE}"
      ;;
    status)
      status_service "router" "${ROUTER_PID_FILE}" "${ROUTER_LOG_FILE}"
      status_service "gateway" "${GATEWAY_PID_FILE}" "${GATEWAY_LOG_FILE}"
      status_service "bot" "${BOT_PID_FILE}" "${BOT_LOG_FILE}"
      status_service "nlp" "${NLP_PID_FILE}" "${NLP_LOG_FILE}"
      ;;
    logs)
      touch "${GATEWAY_LOG_FILE}" "${BOT_LOG_FILE}" "${NLP_LOG_FILE}" "${ROUTER_LOG_FILE}"
      tail -n 100 -f "${GATEWAY_LOG_FILE}" "${BOT_LOG_FILE}" "${NLP_LOG_FILE}" "${ROUTER_LOG_FILE}"
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"

