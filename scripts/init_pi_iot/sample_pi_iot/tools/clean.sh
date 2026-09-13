#!/bin/bash
# ==============================================================================
# File: clean.sh
# Brief: 開發者工具 - 清除 WSL 模擬與打包過程產生的暫存檔與輸出檔
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 可以隨時隨地執行此腳本來淨化專案目錄
# ==============================================================================
echo "===================================================="
echo "  __PROJECT_NAME__ - Dev Workspace Cleaner"
echo "===================================================="

# 取得專案根目錄
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
cd "$PROJECT_ROOT"

echo "[CLEAN] Project root resolved to: $PROJECT_ROOT"

# 刪除 Python 編譯快取目錄 (__pycache__)
echo "[CLEAN] Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 刪除 WSL 模擬測試產生的觸發與臨時文字檔
echo "[CLEAN] Removing mock hardware trigger files..."
rm -f *trigger.txt
rm -f data/*.txt

# 刪除舊版的根目錄打包檔 (為了相容過渡期清理殘留)
echo "[CLEAN] Removing legacy build files from root (if any)..."
rm -f install.tar.gz update.tar.gz ota_manifest.json

# 刪除全新的 output 輸出目錄
if [ -d "output" ]; then
    echo "[CLEAN] Removing /output build directory..."
    rm -rf output
fi

echo "[SUCCESS] Workspace cleanup complete! ✨"
echo "===================================================="