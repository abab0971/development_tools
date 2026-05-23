#!/bin/bash

TARGET_DIR="${1:-.}"
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
DEFAULT_AUTHOR="Author (Author@mycompany.com)"

echo "📂 Preparing to create Pi (IoT Core) Project in: ${TARGET_DIR}"
mkdir -p "${TARGET_DIR}"
cd "${TARGET_DIR}" || exit 1
ABS_PATH=$(pwd)

# Generic multi-format header injection function with '=' fence line
create_file() {
    local filepath=$1
    local brief=$2
    local filename=$(basename "$filepath")
    local ext="${filename##*.}"
    ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

    if [[ "$filename" == "Dockerfile" || "$filename" == "docker-compose.yml" || "$filename" == ".env" || "$filename" == ".gitignore" || "$filename" == "requirements.txt" || "$filename" == ".gitkeep" ]]; then
        ext="hash"
    fi

    case "$ext" in
        py)
            cat << EOF > "$filepath"
# -*- coding: utf-8 -*-
# ==============================================================================
# File: ${filename}
# Brief: ${brief}
# Author: ${DEFAULT_AUTHOR}
# Created Time: ${CURRENT_TIME}
# Copyright: Copyright (c) 2026 公司名 (MyCompany Co., Ltd.)
#            All rights reserved.
# Notice: 
# ==============================================================================
EOF
            ;;
        sh|cfg|ini|txt|hash)
            cat << EOF > "$filepath"
# ==============================================================================
# File: ${filename}
# Brief: ${brief}
# Author: ${DEFAULT_AUTHOR}
# Created Time: ${CURRENT_TIME}
# Copyright: Copyright (c) 2026 公司名 (MyCompany Co., Ltd.)
#            All rights reserved.
# Notice: 
# ==============================================================================
EOF
            ;;
        c|h|css|js)
            cat << EOF > "$filepath"
/* ==============================================================================
 * File: ${filename}
 * Brief: ${brief}
 * Author: ${DEFAULT_AUTHOR}
 * Created Time: ${CURRENT_TIME}
 * Copyright: Copyright (c) 2026 公司名 (MyCompany Co., Ltd.)
 *            All rights reserved.
 * Notice: 
 * ============================================================================== */
EOF
            ;;
        html|md|xml)
            cat << EOF > "$filepath"
EOF
            ;;
    esac
}

# Create Directory Layout
mkdir -p data app/common app/config/gpio app/core app/database app/infrastructure/gpio app/infrastructure/mqtt app/tests

# Empty directory tracking placeholder
touch data/.gitkeep

# Populate Root Files with Project Head
create_file ".env" "環境變數與安全金鑰配置檔"
create_file ".gitignore" "Git 版本控制忽略檔案清單"
create_file "Dockerfile" "跨平台多階段 Docker 映像檔編譯藍圖"
create_file "docker-compose.yml" "多容器服務邊排與依賴管理設定檔"
create_file "requirements.txt" "Python 專案依賴套件清單"
create_file "README.md" "專案部署環境與核心操作說明文件"

# Populate Python App Files with Project Head
create_file "app/__init__.py" "應用程式根套件初始化宣告"
create_file "app/main.py" "系統背景運行與 IoT 核心邏輯唯一的啟動進入點"
create_file "app/config.py" "系統全域設定模組，負責載入與強制驗證設定檔"

create_file "app/common/__init__.py" "通用工具套件初始化宣告"
create_file "app/common/utils.py" "全域純函數、通用輔助與運算工具模組"

create_file "app/core/__init__.py" "核心領域業務邏輯套件初始化宣告"
create_file "app/core/hardware.py" "實體硬體狀態機與核心業務行為邏輯實作"
create_file "app/core/interfaces.py" "核心層硬體驅動與外部通知服務之抽象介面定義"

create_file "app/database/__init__.py" "資料儲存與適配層套件初始化宣告"
create_file "app/database/connection.py" "SQLite 資料庫連線初始化與連線池管理"
create_file "app/database/crud.py" "資料庫通用增刪查改（CRUD）常規操作實作"

create_file "app/infrastructure/__init__.py" "基礎設施層套件初始化宣告"
create_file "app/infrastructure/gpio/__init__.py" "GPIO Standalone 獨立驅件套件初始化"
create_file "app/infrastructure/gpio/gpio_drivers.py" "GPIO 輸出輸入控制器實體驅動程式碼"
create_file "app/infrastructure/mqtt/__init__.py" "MQTT Standalone 獨立通訊套件初始化"
create_file "app/infrastructure/mqtt/mqtt_client.py" "MQTT 客戶端實體通訊協定整合實作"

create_file "app/tests/__init__.py" "獨立測試套件初始化宣告"
create_file "app/tests/conftest.py" "Pytest 全域配置與本機虛擬硬體 Mock 註冊"
create_file "app/tests/test_core.py" "針對核心硬體邏輯與狀態機的單元測試"

# 🎯 【本次優化】先使用 create_file 建立標準隔離標頭，再使用 >> 附加內容
create_file "app/config/gpio/gpio.cfg" "GPIO 特定功能獨立引腳硬體設定檔"
cat << EOF >> "app/config/gpio/gpio.cfg"

[PIN_MAPPING]
LED_GREEN     = 1
LED_RED       = 2
LED_YELLOW    = 3
EOF

echo "✅ Pi (IoT Core) Project generated with standard fenced Project Head!"
echo "👉 Project Path: ${ABS_PATH}"