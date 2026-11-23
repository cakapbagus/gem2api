#!/usr/bin/env bash
# ==============================================================================
# Gemini Web2API Gateway Service Controller (Linux • Termux • macOS • WSL)
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${PROJECT_DIR}/logs"
COOKIES_DIR="${PROJECT_DIR}/cookies"
PID_FILE="${LOG_DIR}/gateway.pid"
STDOUT_LOG="${LOG_DIR}/gateway_stdout.log"
PORT=10012
HOST="0.0.0.0"

mkdir -p "${LOG_DIR}" "${COOKIES_DIR}"

# Locate Python 3 interpreter
find_python() {
    if [ -n "${VIRTUAL_ENV}" ] && [ -x "${VIRTUAL_ENV}/bin/python" ]; then
        echo "${VIRTUAL_ENV}/bin/python"
    elif [ -x "${PROJECT_DIR}/venv/bin/python" ]; then
        echo "${PROJECT_DIR}/venv/bin/python"
    elif [ -x "${PROJECT_DIR}/.venv/bin/python" ]; then
        echo "${PROJECT_DIR}/.venv/bin/python"
    elif command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        echo "python"
    else
        echo ""
    fi
}

PYTHON_BIN=$(find_python)

check_python() {
    if [ -z "${PYTHON_BIN}" ]; then
        echo "[-] Error: Python 3 is required but not found in PATH."
        echo "    Please install Python 3 (e.g. 'pkg install python' or 'apt install python3')."
        exit 1
    fi
}

get_pid() {
    if [ -f "${PID_FILE}" ]; then
        local pid
        pid=$(cat "${PID_FILE}" 2>/dev/null)
        if [ -n "${pid}" ] && kill -0 "${pid}" 2>/dev/null; then
            echo "${pid}"
            return 0
        fi
    fi
    # Fallback search by process name
    local found_pid
    found_pid=$(pgrep -f "gemini_web2api" 2>/dev/null | head -n 1)
    if [ -n "${found_pid}" ]; then
        echo "${found_pid}"
        return 0
    fi
    return 1
}

start() {
    check_python

    local pid
    if pid=$(get_pid); then
        echo "[!] Gemini Web2API is already running (PID: ${pid})."
        echo "    Local URL:  http://127.0.0.1:${PORT}/v1"
        echo "    Dashboard:  http://127.0.0.1:${PORT}/"
        return 0
    fi

    echo "[*] Starting Gemini Web2API Gateway on port ${PORT}..."
    cd "${PROJECT_DIR}" || exit 1

    # Check for httpx
    if ! "${PYTHON_BIN}" -c "import httpx" >/dev/null 2>&1; then
        echo "[!] Notice: Required package 'httpx' is missing."
        echo "    Attempting to install: pip install httpx..."
        "${PYTHON_BIN}" -m pip install httpx || true
    fi

    # Spawn daemon safely across Linux, Termux, macOS
    if command -v setsid >/dev/null 2>&1; then
        setsid "${PYTHON_BIN}" -m gemini_web2api --port "${PORT}" --host "${HOST}" </dev/null >> "${STDOUT_LOG}" 2>&1 &
        local new_pid=$!
    elif command -v nohup >/dev/null 2>&1; then
        nohup "${PYTHON_BIN}" -m gemini_web2api --port "${PORT}" --host "${HOST}" </dev/null >> "${STDOUT_LOG}" 2>&1 &
        local new_pid=$!
    else
        "${PYTHON_BIN}" -m gemini_web2api --port "${PORT}" --host "${HOST}" </dev/null >> "${STDOUT_LOG}" 2>&1 &
        local new_pid=$!
    fi

    disown "${new_pid}" 2>/dev/null || true
    echo "${new_pid}" > "${PID_FILE}"

    # Wait for gateway to initialize
    local timeout=10
    while [ ${timeout} -gt 0 ]; do
        if curl -s "http://127.0.0.1:${PORT}/v1" >/dev/null 2>&1; then
            echo "[+] Gemini Web2API Gateway started successfully!"
            echo "    PID:        ${new_pid}"
            echo "    Local URL:  http://127.0.0.1:${PORT}/v1"
            echo "    Dashboard:  http://127.0.0.1:${PORT}/"
            echo "    Log File:   ${STDOUT_LOG}"
            echo ""
            echo "💡 Tip: Open the dashboard in your browser to add accounts or test models."
            return 0
        fi
        sleep 1
        timeout=$((timeout - 1))
    done

    echo "[!] Warning: Process spawned (PID: ${new_pid}), but HTTP port not yet responding."
    echo "    Check logs with: ./run.sh logs"
}

run_foreground() {
    check_python
    echo "[*] Running Gemini Web2API Gateway in foreground on port ${PORT}..."
    cd "${PROJECT_DIR}" || exit 1
    exec "${PYTHON_BIN}" -m gemini_web2api --port "${PORT}" --host "${HOST}"
}

stop() {
    local pid
    if ! pid=$(get_pid); then
        echo "[*] Gemini Web2API is not running."
        rm -f "${PID_FILE}"
        return 0
    fi

    echo "[*] Stopping Gemini Web2API (PID: ${pid})..."
    kill -15 "${pid}" 2>/dev/null || true
    local timeout=5
    while [ ${timeout} -gt 0 ]; do
        if ! kill -0 "${pid}" 2>/dev/null; then
            break
        fi
        sleep 1
        timeout=$((timeout - 1))
    done

    if kill -0 "${pid}" 2>/dev/null; then
        echo "[!] Process did not exit gracefully, force killing..."
        kill -9 "${pid}" 2>/dev/null || true
    fi

    rm -f "${PID_FILE}"
    echo "[+] Gateway stopped."
}

status() {
    local pid
    if pid=$(get_pid); then
        echo "[+] Gemini Web2API Gateway is RUNNING (PID: ${pid})"
        echo "    Local Address: http://127.0.0.1:${PORT}/v1"
        echo "    Dashboard:     http://127.0.0.1:${PORT}/"
        echo ""
        echo "--- Health Status ---"
        curl -s "http://127.0.0.1:${PORT}/v1" | python3 -m json.tool 2>/dev/null || echo "Gateway online"
    else
        echo "[-] Gemini Web2API Gateway is STOPPED."
    fi
}

restart() {
    stop
    sleep 1
    start
}

logs() {
    if [ -f "${STDOUT_LOG}" ]; then
        tail -f -n 35 "${STDOUT_LOG}"
    else
        echo "[!] Log file not found at ${STDOUT_LOG}"
    fi
}

test_gateway() {
    check_python
    echo "[*] Running end-to-end diagnostics and test suite..."
    cd "${PROJECT_DIR}" && "${PYTHON_BIN}" -m unittest tests.test_end_to_end
}

case "$1" in
    start)
        start
        ;;
    run|fg)
        run_foreground
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    test)
        test_gateway
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|run|test}"
        echo ""
        echo "Commands:"
        echo "  start    - Start gateway as background daemon"
        echo "  stop     - Stop background gateway daemon"
        echo "  restart  - Restart gateway daemon"
        echo "  status   - View process status and health check"
        echo "  logs     - Stream live gateway output logs"
        echo "  run      - Run in foreground (for debugging)"
        echo "  test     - Run automated test suite"
        exit 1
        ;;
esac
