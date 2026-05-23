#!/bin/bash

TARGET_DIR="${1:-.}"
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
DEFAULT_AUTHOR="Author (Author@mycompany.com)"

echo "📂 Preparing to create Pi (IoT + Web Portal) Project in: ${TARGET_DIR}"
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

    if [[ "$filename" == "Dockerfile" || "$filename" == "docker-compose.yml" || "$filename" == ".env" || "$filename" == ".gitignore" || "$filename" == "requirements.txt" || "$filename" == ".gitkeep" || "$filename" == "mosquitto.conf" ]]; then
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
#           All rights reserved.
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
        *)
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
    esac
}

# Create Directories
mkdir -p data mosquitto/config
mkdir -p app/common app/config/gpio app/core app/database app/infrastructure/gpio app/infrastructure/mqtt app/tests
mkdir -p app/api/v1 app/static/css app/static/js app/templates

touch data/.gitkeep
touch app/static/css/.gitkeep
touch app/static/js/.gitkeep

# Root Configuration Files
create_file ".env" "環境變數與外部服務安全憑證設定檔"
create_file ".gitignore" "Git 版本控制檔案忽略規則清單"
create_file "Dockerfile" "多階段交叉編譯與適配樹莓派之 Docker 藍圖"
create_file "docker-compose.yml" "應用程式與 Mosquitto 多容器服務編排配置"
create_file "requirements.txt" "Python 依賴套件核心清單"
create_file "README.md" "項目部署部署與運作操作說明文件"
create_file "mosquitto/config/mosquitto.conf" "Mosquitto MQTT Broker 伺服器通訊權限設定檔"

# Application Source Files
create_file "app/__init__.py" "應用程式根套件初始化宣告"
create_file "app/main.py" "FastAPI 應用程式載入、路由註冊與啟動進入點"
create_file "app/config.py" "利用 Pydantic 載入並動態解析硬體設定之配置模組"

create_file "app/common/__init__.py" "通用工具套件初始化宣告"
create_file "app/common/utils.py" "全域純函數與數據格式轉換工具模組"

create_file "app/core/__init__.py" "核心層套件初始化宣告"
create_file "app/core/hardware.py" "硬體管理器、狀態機運作與回收箱業務核心邏輯"
create_file "app/core/interfaces.py" "核心層與外部驅動解耦之抽象介面合約定義"

create_file "app/api/__init__.py" "外部傳輸與通訊接口層初始化宣告"
create_file "app/api/v1/__init__.py" "API 版本 1 控制套件初始化"
create_file "app/api/v1/endpoints.py" "FastAPI HTTP RESTful 遠端控制 API 路由接口"
create_file "app/api/websocket.py" "WebSocket 即時雙向數據推播通訊接口"

create_file "app/database/__init__.py" "資料儲存層套件初始化宣告"
create_file "app/database/connection.py" "SQLite 實體連線初始化與連線池生命週期管理"
create_file "app/database/crud.py" "針對業務歷史紀錄之增刪查改 SQL 操作實作"

create_file "app/infrastructure/__init__.py" "基礎設施層套件初始化宣告"
create_file "app/infrastructure/gpio/__init__.py" "GPIO 獨立驅動套件初始化"
create_file "app/infrastructure/gpio/gpio_drivers.py" "獨立的 GPIO 輸出輸入實體控制驅動"
create_file "app/infrastructure/mqtt/__init__.py" "MQTT 獨立通訊套件初始化"
create_file "app/infrastructure/mqtt/mqtt_client.py" "獨立的 MQTT Client 訊息訂閱與發送實作"

create_file "app/templates/index.html" "智慧回收箱遠端監控儀表板後端渲染網頁範本"

create_file "app/tests/__init__.py" "測試套件初始化宣告"
create_file "app/tests/conftest.py" "Pytest 全域配置、虛擬硬體與 API 測試 Mock 註冊"
create_file "app/tests/test_api.py" "針對 FastAPI HTTP/WebSocket 路由接口之單元測試"
create_file "app/tests/test_core.py" "針對核心業務與硬體管理器之單元測試"

# 🎯 【本次優化】先使用 create_file 建立標準隔離標頭，再使用 >> 附加內容
create_file "app/config/gpio/gpio.cfg" "GPIO 特定功能獨立引腳硬體設定檔"
cat << EOF >> "app/config/gpio/gpio.cfg"

[PIN_MAPPING]
LED_GREEN     = 1
LED_RED       = 2
LED_YELLOW    = 3
EOF

echo "✅ Pi (IoT + Web Portal) Project generated with standard fenced Project Head!"
echo "👉 Project Path: ${ABS_PATH}"