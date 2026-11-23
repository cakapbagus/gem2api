#!/usr/bin/env bash
# ==============================================================================
# Gemini Web2API Gateway Service Controller for Android Termux
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${PROJECT_DIR}/logs"
PID_FILE="${LOG_DIR}/gateway.pid"
STDOUT_LOG="${LOG_DIR}/gateway_stdout.log"
PORT=10012
HOST="127.0.0.1"

mkdir -p "${LOG_DIR}"

get_pid() {
    if [ -f "${PID_FILE}" ]; then
        local pid
        pid=$(cat "${PID_FILE}" 2>/dev/null)
        if [ -n "${pid}" ] && kill -0 "${pid}" 2>/dev/null; then
            echo "${pid}"
            return 0
        fi
    fi
    # Fallback process search
    local found_pid
    found_pid=$(pgrep -f "gemini_web2api" | head -n 1)
    if [ -n "${found_pid}" ]; then
        echo "${found_pid}"
        return 0
    fi
    return 1
}

start() {
    local pid
    if pid=$(get_pid); then
        echo "[!] Gemini Web2API is already running (PID: ${pid})."
        echo "    Endpoint: http://${HOST}:${PORT}/v1"
        return 0
    fi

    echo "[*] Starting Gemini Web2API Gateway on http://${HOST}:${PORT}..."
    cd "${PROJECT_DIR}" || exit 1
    setsid python3 -m gemini_web2api --port "${PORT}" </dev/null >> "${STDOUT_LOG}" 2>&1 &
    local new_pid=$!
    disown "${new_pid}" 2>/dev/null || true
    echo "${new_pid}" > "${PID_FILE}"

    # Wait for gateway to initialize
    local timeout=8
    while [ ${timeout} -gt 0 ]; do
        if curl -s "http://${HOST}:${PORT}/v1" >/dev/null 2>&1; then
            echo "[+] Gemini Web2API Gateway started successfully!"
            echo "    PID:        ${new_pid}"
            echo "    Local URL:  http://${HOST}:${PORT}/v1"
            echo "    Dashboard:  http://${HOST}:${PORT}/"
            echo "    Log File:   ${STDOUT_LOG}"
            return 0
        fi
        sleep 1
        timeout=$((timeout - 1))
    done

    echo "[!] Warning: Gateway process spawned (PID: ${new_pid}), but HTTP port not yet responding."
    echo "    Check logs with: bash ${PROJECT_DIR}/gemini-gateway.sh logs"
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
        echo "    Local Address: http://${HOST}:${PORT}/v1"
        echo "    Dashboard:     http://${HOST}:${PORT}/"
        echo ""
        echo "--- Health Check ---"
        curl -s "http://${HOST}:${PORT}/v1" | python3 -m json.tool 2>/dev/null || echo "Unable to parse /v1 response"
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
        tail -f -n 30 "${STDOUT_LOG}"
    else
        echo "[!] Log file not found at ${STDOUT_LOG}"
    fi
}

test_gateway() {
    echo "[*] Running diagnostic self-check..."
    cd "${PROJECT_DIR}" && python3 -m gemini_web2api --test
}

case "$1" in
    start)
        start
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
        echo "Usage: $0 {start|stop|restart|status|logs|test}"
        exit 1
        ;;
esac
