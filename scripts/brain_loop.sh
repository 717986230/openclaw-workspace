#!/bin/bash
# Erbing 大脑守护进程启动脚本
# 用法: ./brain_loop.sh [mode]
#   start   - 启动守护进程 (后台)
#   stop    - 停止守护进程
#   status  - 查看状态
#   once    - 单次运行

MODE=${1:-once}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/Users/xinglong/openclaw-workspace/memory/events"
PID_FILE="/tmp/erbing_brain.pid"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/brain_daemon.log"
}

start_daemon() {
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            log "大脑已在运行 (PID: $OLD_PID)"
            return
        fi
    fi
    
    log "🚀 启动 Erbing 大脑守护进程..."
    
    # 后台运行大脑循环
    (
        while true; do
            python3 "$SCRIPT_DIR/brain_core.py" >> "$LOG_DIR/brain_cycle.log" 2>&1
            log "大脑循环完成，60秒后继续..."
            sleep 60
        done
    ) &
    
    NEW_PID=$!
    echo $NEW_PID > "$PID_FILE"
    log "大脑守护进程已启动 (PID: $NEW_PID)"
}

stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            log "🛑 停止大脑守护进程 (PID: $PID)..."
            kill "$PID"
            rm "$PID_FILE"
            log "大脑守护进程已停止"
        else
            log "大脑守护进程未在运行"
            rm -f "$PID_FILE"
        fi
    else
        log "无PID文件，无法停止"
    fi
}

status_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            log "🧠 大脑守护进程运行中 (PID: $PID)"
            return
        fi
    fi
    log "💤 大脑守护进程未运行"
}

case "$MODE" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    status)
        status_daemon
        ;;
    once|*)
        log "🧠 运行单次大脑循环..."
        python3 "$SCRIPT_DIR/brain_core.py"
        ;;
esac