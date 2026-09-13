#!/bin/bash
# ==============================================================================
# File: init_pi_iot.sh
# Brief: Raspberry Pi (IoT Core) 專案結構初始化工具
# Author: development_tools
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 批次調度 sample_pi_iot 樣板建立新 Pi IoT 專案之管理腳本==============================================================================
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SAMPLE_DIR="${SCRIPT_DIR}/sample_pi_iot"
TARGET_DIR="${1:-.}"

# 確保目標目錄存在
mkdir -p "${TARGET_DIR}"
cd "${TARGET_DIR}" || exit 1
ABS_PATH=$(pwd)

# 自動推導專案預設名稱
DEFAULT_PROJ_NAME=$(basename "${ABS_PATH}")
if [ "$DEFAULT_PROJ_NAME" == "." ] || [ "$DEFAULT_PROJ_NAME" == "/" ] || [ -z "$DEFAULT_PROJ_NAME" ]; then
    DEFAULT_PROJ_NAME="my_pi_iot_project"
fi

if [ -n "$2" ]; then
    INPUT_PROJECT_NAME="$2"
else
    echo ""
    read -p "Enter Project Name (Default: ${DEFAULT_PROJ_NAME}): " INPUT_PROJECT_NAME
fi

PROJECT_NAME="${INPUT_PROJECT_NAME:-$DEFAULT_PROJ_NAME}"
PROJECT_NAME=$(echo "$PROJECT_NAME" | tr ' ' '_')
PROJ_NAME_LOWER=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9_-')
PROJ_NAME_UPPER=$(echo "$PROJECT_NAME" | tr '[:lower:]' '[:upper:]' | tr -cd 'A-Z0-9_-')

echo "🚀 Initializing Pi IoT project [${PROJECT_NAME}] at: ${ABS_PATH}"

# 1. 驗證樣板目錄並進行實體複製
if [ ! -d "${SAMPLE_DIR}" ]; then
    echo "[ERROR] Sample template directory not found at: ${SAMPLE_DIR}"
    exit 1
fi

cp -r "${SAMPLE_DIR}/." "${ABS_PATH}/"

# 2. 批次替換多維度佔位符 (完整保留原始檔內註釋)
find "${ABS_PATH}" -type f \( -name "*.json" -o -name "*.yml" -o -name "*.cfg" -o -name "*.sh" -o -name "*.py" -o -name "*.md" \) -exec sed -i "s/__PROJECT_NAME__/${PROJECT_NAME}/g" {} +
find "${ABS_PATH}" -type f \( -name "*.json" -o -name "*.yml" -o -name "*.cfg" -o -name "*.sh" -o -name "*.py" -o -name "*.md" \) -exec sed -i "s/__PROJ_NAME_LOWER__/${PROJ_NAME_LOWER}/g" {} +
find "${ABS_PATH}" -type f \( -name "*.json" -o -name "*.yml" -o -name "*.cfg" -o -name "*.sh" -o -name "*.py" -o -name "*.md" \) -exec sed -i "s/__PROJ_NAME_UPPER__/${PROJ_NAME_UPPER}/g" {} +

# 賦予工具腳本執行權限
chmod +x "${ABS_PATH}/tools/"*.sh 2>/dev/null || true

echo "✅ Project [${PROJECT_NAME}] initialized successfully with full sample template!"