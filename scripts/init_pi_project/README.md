# 🚀 Raspberry Pi + FastAPI 專案結構初始化工具

此工具用於一鍵生成基於 **乾淨架構 (Clean Architecture)** 精神設計的樹莓派物聯網 (IoT) 專案。透過解耦硬體驅動、業務邏輯與外部傳輸協定，確保系統在 WSL 虛擬環境中易於測試，並能無縫部署至實體樹莓派。

---

## 📂 生成的專案結構說明

執行 `init_pi_project.sh` 後，將會自動生成以下目錄與檔案。每一層都有其核心職責，請遵循此規範進行開發：

```text
test_project/
├── .env                  # 環境變數設定檔（管理機密金鑰、主機 IP、資料庫路徑與 MQTT 憑證）
├── .gitignore            # Git 忽略清單（自動排除 __pycache__、.pytest_cache、SQLite db 等暫存）
├── Dockerfile            # 跨平台 Docker 藍圖（採用多階段編譯，自適應 WSL x86_64 與樹莓派 ARM64）
├── docker-compose.yml    # 多容器編排（一鍵管理 Python App 與輕量化 Mosquitto MQTT Broker 服務）
├── requirements.txt      # Python 核心套件依賴清單（FastAPI, GPIO Zero, smbus2, pyserial 等）
├── README.md             # 專案部署說明（記錄 Docker 常用指令與環境變數配置）
│
├── data/                 # 資料持久化目錄（由 Docker Volume 映射，防止容器重啟資料遺失）
│   └── pi.db             # 自動生成的 SQLite 實體資料庫檔案
│
├── mosquitto/            # MQTT Broker 獨立設定檔目錄
│   └── config/
│       └── mosquitto.conf # Mosquitto 伺服器設定（控制匿名連線、Listen Port 等）
│
└── app/                  # 應用程式原始碼主目錄（架構核心分層）
    ├── __init__.py       # 將 app 宣告為一個可被 import 的 Python 套件
    ├── main.py           # 系統唯一的啟動進入點（在此用 Uvicorn 載入核心與執行依賴注入）
    ├── config.py         # 全域設定模組（利用 Pydantic 載入並強制驗證 .env 的變數型態）
    │
    ├── core/             # 🔥【核心層 (Domain/Use Cases)】純粹的業務與硬體邏輯
    │   ├── __init__.py
    │   ├── hardware.py   # GPIO Zero 外包裝（定義 LED 控制、感測器觸發等核心行為邏輯）
    │   └── interfaces.py # 💡 抽象介面定義（定義通知服務、資料庫儲存的抽象類別 Abstract Class）
    │                     # 🎯 註：核心層不 import 任何基礎設施套件（如 paho-mqtt），確保可用 Mock 測試
    │
    ├── infrastructure/   # 🔌【基礎設施層 (Infrastructure)】外部工具與硬體通訊的實體操作
    │   ├── __init__.py
    │   ├── mqtt_client.py# 💡 MQTT 客戶端實作（在此 import paho-mqtt 並繼承 core/interfaces 介面）
    │   ├── serial_io.py  # 序列埠 (pyserial) 實體驅動讀寫實作
    │   └── i2c_bus.py    # I2C 總線 (smbus2) 實體驅動讀寫實作
    │
    ├── database/         # 💾【資料與儲存適配層 (Interface Adapters)】
    │   ├── __init__.py
    │   ├── connection.py # SQLite 資料庫連線初始化、連線池 (Session) 管理
    │   └── crud.py       # 定義資料增刪查改（Create, Read, Update, Delete）的通用 SQL 運作
    │
    ├── api/              # 🌐【外部傳輸層 (User Interface / Transports)】API 與通訊接口
    │   ├── __init__.py
    │   ├── v1/           # API 版本控制（確保未來系統升級時的舊版相容性）
    │   │   └── endpoints.py # 定義各種 HTTP RESTful API（呼叫 core/hardware 執行硬體動作）
    │   └── websocket.py  # WebSocket 傳輸接口（用於將硬體狀態、感測器數據即時推送到網頁前端）
    │
    ├── static/           # 🎨【網頁前端靜態資源】（由 FastAPI StaticFiles 直接掛載）
    │   ├── css/          # 存放 Bootstrap 等 CSS 樣式表
    │   └── js/           # 存放前端 JavaScript（處理 WebSocket 接收、非同步 fetch 請求）
    │
    ├── templates/        # 📄【後端網頁範本】（由 FastAPI Jinja2Templates 渲染）
    │   └── index.html    # 樹莓派控制儀表板網頁畫面（整合前端 UI 與硬體按鈕）
    │
    └── tests/            # 🧪【獨立測試層 (Test Suite)】
        ├── __init__.py
        ├── conftest.py   # Pytest 全域配置（在此配置 Mock 硬體與虛擬環境變數，使其可在 WSL 順利測試）
        ├── test_api.py   # 針對 FastAPI 路由與通訊接口的單元測試
        └── test_core.py  # 針對核心硬體邏輯、狀態機的單元測試
```