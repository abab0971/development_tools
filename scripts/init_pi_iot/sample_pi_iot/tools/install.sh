#!/bin/bash
# ==============================================================================
# File: install.sh
# Brief: 通用樹莓派 IoT 核心出廠與現場安裝腳本 (A/B Slot 佈建與 Systemd 註冊)
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 本腳本需以 sudo 權限執行
# ==============================================================================

# 嚴格模式：遇到錯誤即停止
set -e

# 定義目標安裝路徑
BASE_DIR="/opt/__PROJ_NAME_LOWER__"
SLOT_A="$BASE_DIR/slot_A"
SLOT_B="$BASE_DIR/slot_B"
DATA_DIR="$BASE_DIR/data"
CURRENT_LINK="$BASE_DIR/current"
SERVICE_FILE="/etc/systemd/system/__PROJ_NAME_LOWER__.service"

echo "===================================================="
echo "  __PROJECT_NAME__ - Factory Installation Tool  "
echo "===================================================="

# 1. 權限檢查
if [ "$EUID" -ne 0 ]; then 
  echo "[ERROR] Please run this script as root (sudo)."
  exit 1
fi

# 2. 智慧判斷安裝來源 (Tarball 壓縮包 或 解壓後的資料夾)
SRC_PATH="${1:-}"
IS_TARBALL=false

if [ -z "$SRC_PATH" ]; then
    # 若未指定路徑，取得腳本自身所在的實體目錄
    SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
    
    # 策略 A：優先尋找與 install.sh 放在「同一個目錄下」的 install.tar.gz
    if [ -f "$SCRIPT_DIR/install.tar.gz" ]; then
        SRC_PATH="$SCRIPT_DIR/install.tar.gz"
        IS_TARBALL=true
    # 策略 B：其次尋找「執行當前目錄下」的 install.tar.gz
    elif [ -f "./install.tar.gz" ]; then
        SRC_PATH="./install.tar.gz"
        IS_TARBALL=true
    # 策略 C：退回舊有開發邏輯 (假設腳本位於已經解壓的專案 tools/ 內)
    else
        PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
        if [ -f "$PROJECT_ROOT/docker-compose.pi.yml" ]; then
            SRC_PATH="$PROJECT_ROOT"
        else
            echo "[ERROR] Cannot find install.tar.gz or a valid project root."
            echo "Usage: sudo ./install.sh [path/to/install.tar.gz | path/to/project_dir]"
            exit 1
        fi
    fi
else
    # 若使用者有帶入指定路徑，進行驗證
    if [ -f "$SRC_PATH" ] && [[ "$SRC_PATH" == *.tar* ]]; then
        IS_TARBALL=true
    elif [ -d "$SRC_PATH" ]; then
        IS_TARBALL=false
    else
        echo "[ERROR] Specified path '$SRC_PATH' is invalid."
        exit 1
    fi
fi

echo "[INFO] Installation Source resolved to: $SRC_PATH"

# 3. 建立 A/B Slot 與資料護城河結構
echo "[INFO] Creating A/B Slot directories..."
mkdir -p "$SLOT_A"
mkdir -p "$SLOT_B"
mkdir -p "$DATA_DIR/logs"

# 4. 複製或解壓檔案至 Slot A
echo "[INFO] Deploying application files to Slot A..."
if [ "$IS_TARBALL" = true ]; then
    # 🎯 直接從 tarball 解壓縮到 Slot A (剝除第一層目錄 __PROJECT_NAME__)
    tar -xzf "$SRC_PATH" --strip-components=1 -C "$SLOT_A"
else
    # 🎯 從目錄複製 (不再排除 tools 目錄，確保未來可以正常使用 uninstall.sh)
    rsync -av --exclude='.git' --exclude='venv' --exclude='.venv' --exclude='data' --exclude='install.tar.gz' --exclude='update.tar.gz' --exclude='.env' "$SRC_PATH/" "$SLOT_A/"
fi

# 5. 建立軟連結 (Symlink)，初始指向 Slot A
echo "[INFO] Setting up symlink to Slot A..."
ln -sfn "$SLOT_A" "$CURRENT_LINK"

# 6. 複製守護行程腳本至根目錄 (不受 A/B 槽更換影響)
echo "[INFO] Deploying OTA Watchdog script..."
cp "$SLOT_A/tools/watchdog.sh" "$BASE_DIR/watchdog.sh"
chmod +x "$BASE_DIR/watchdog.sh"

# 7. 註冊 systemd 開機自啟動服務
echo "[INFO] Registering systemd auto-start service..."
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=__PROJECT_NAME__ OTA Watchdog and Docker Manager
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=$BASE_DIR
ExecStart=$BASE_DIR/watchdog.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 8. 重載 systemd 並啟用服務
systemctl daemon-reload
systemctl enable __PROJ_NAME_LOWER__.service

echo "[SUCCESS] Installation complete!"
echo "[INFO] Systemd service '__PROJ_NAME_LOWER__' enabled. It will start on the next boot."
echo "[INFO] To start immediately, run: sudo systemctl start __PROJ_NAME_LOWER__"
echo "===================================================="