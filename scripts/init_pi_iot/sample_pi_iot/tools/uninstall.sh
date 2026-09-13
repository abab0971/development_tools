#!/bin/bash
# ==============================================================================
# File: uninstall.sh
# Brief: 通用樹莓派 IoT 核心無痕卸載腳本 (移除 A/B Slot、背景容器與 Systemd 註冊)
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 本腳本需以 sudo 權限執行
# ==============================================================================

# 嚴格模式：遇到錯誤即停止
set -e

BASE_DIR="/opt/__PROJ_NAME_LOWER__"
CURRENT_LINK="$BASE_DIR/current"
ENV_FILE="$BASE_DIR/data/.env"
SERVICE_FILE="/etc/systemd/system/__PROJ_NAME_LOWER__.service"

echo "===================================================="
echo "  __PROJECT_NAME__ - Uninstallation Tool  "
echo "===================================================="

# 1. 權限檢查
if [ "$EUID" -ne 0 ]; then 
  echo "[ERROR] Please run this script as root (sudo)."
  exit 1
fi

# 2. 二次確認防呆機制
echo "[WARNING] This action will COMPLETELY REMOVE the __PROJECT_NAME__ system."
echo "[WARNING] This includes all firmware versions, SQLite databases, and Logs in $BASE_DIR!"
read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "[INFO] Uninstallation aborted by user."
    exit 0
fi

# 3. 停止與註銷 Systemd 守護行程 (watchdog.sh)
if systemctl is-active --quiet __PROJ_NAME_LOWER__.service; then
    echo "[INFO] Stopping Systemd watchdog service..."
    systemctl stop __PROJ_NAME_LOWER__.service
fi

if systemctl is-enabled --quiet __PROJ_NAME_LOWER__.service 2>/dev/null; then
    echo "[INFO] Disabling Systemd watchdog service..."
    systemctl disable __PROJ_NAME_LOWER__.service
fi

if [ -f "$SERVICE_FILE" ]; then
    echo "[INFO] Removing Systemd service configuration..."
    rm -f "$SERVICE_FILE"
    systemctl daemon-reload
fi

# ==============================================================================
# 4. 優雅關閉並移除背景的 Docker 容器
# ==============================================================================
if [ -d "$CURRENT_LINK" ] && [ -f "$ENV_FILE" ]; then
    echo "[INFO] Stopping running Docker containers..."
    # 讀取持久化環境變數
    source "$ENV_FILE"
    
    if [ -n "$DOCKER_COMPOSE_FILE" ] && [ -f "$CURRENT_LINK/$DOCKER_COMPOSE_FILE" ]; then
        # 🎯 取得真實的槽位名稱 (例如 slot_a)
        CURRENT_SLOT=$(readlink -f "$CURRENT_LINK")
        SLOT_NAME=$(basename "$CURRENT_SLOT" | tr '[:upper:]' '[:lower:]')
        
        # 推算另一個槽位的名稱
        ALT_SLOT_NAME="slot_b"
        if [ "$SLOT_NAME" == "slot_b" ]; then
            ALT_SLOT_NAME="slot_a"
        fi

        echo "[INFO] Shutting down compose project: $SLOT_NAME"
        (cd "$CURRENT_LINK" && docker compose -p "$SLOT_NAME" -f "$DOCKER_COMPOSE_FILE" down -v) || echo "[WARNING] Failed to stop $SLOT_NAME."
        
        # 雙重保險：把另一個槽的網路和潛在殭屍容器也關了
        echo "[INFO] Shutting down compose project: $ALT_SLOT_NAME (Cleanup)"
        (cd "$CURRENT_LINK" && docker compose -p "$ALT_SLOT_NAME" -f "$DOCKER_COMPOSE_FILE" down -v 2>/dev/null) || true
    fi
fi

# 5. 徹底移除 A/B 槽與資料護城河
if [ -d "$BASE_DIR" ]; then
    echo "[INFO] Removing all application files and data directories..."
    rm -rf "$BASE_DIR"
fi

echo "[SUCCESS] __PROJECT_NAME__ has been completely uninstalled!"
echo "===================================================="