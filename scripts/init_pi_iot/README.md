# 🚀 Raspberry Pi (IoT Core) 專案結構初始化工具

此工具用於一鍵生成基於 **乾淨架構 (Clean Architecture)** 精神設計的樹莓派純硬體通訊與控制核心專案。此架構**不包含任何網頁前端與外部 API 傳輸層**，專門針對 Headless（無螢幕）自動化運作、背景服務、MQTT 邊緣運算節點等輕量化物聯網場景設計，非常適合部署於資源有限的樹莓派環境（如 Raspberry Pi Zero 2W）。

---

## 📂 生成的專案結構說明

執行 `init_pi_iot.sh` 後，將會自動生成以下精簡且解耦的目錄與檔案。每個檔案皆已自動注入標準專案標頭（Head 註釋）：

```text
test_project/
├── .env                  # 環境變數設定檔（管理主機 IP、機密金鑰、全域變數）
├── .gitignore            # Git 忽略清單（自動排除 __pycache__、.pytest_cache 等暫存）
├── Dockerfile            # 跨平台 Docker 藍圖（採用多階段編譯，自適應 WSL x86_64 與樹莓派 ARM64）
├── docker-compose.yml    # 多容器編排（一鍵管理 Python App 與輕量化遠端服務）
├── requirements.txt      # Python 核心套件依賴清單
├── README.md             # 專案部署說明（記錄環境變數設定與 Docker 常用操作指令）
│
├── data/                 # 資料持久化目錄（由 Docker Volume 映射）
│   └── .gitkeep          # 確保真空空目錄能被 Git 追蹤
│
└── app/                  # 應用程式原始碼主目錄
    ├── __init__.py       # 將 app 宣告為一個可被引用的 Python 套件
    ├── main.py           # 系統唯一的啟動進入點（在此載入核心邏輯與執行依賴注入）
    ├── config.py         # 全域設定模組（利用 Pydantic 載入並驗證 .env 的變數型態）
    │
    ├── common/           # 🛠️【通用工具層】不涉及業務與硬體狀態的純函數
    │   ├── __init__.py
    │   └── utils.py      # 通用輔助函式、資料轉換、純數學計算工具
    │
    ├── config/           # ⚙️【特定功能獨立設定檔目錄】
    │   └── gpio/
    │       └── gpio.cfg  # INI 格式的硬體引腳設定檔，將實體腳位與程式碼徹底抽離
    │
    ├── core/             # 🔥【核心層】純粹的業務與硬體控制邏輯
    │   ├── __init__.py
    │   ├── hardware.py   # 核心狀態機與業務核心行為（如箱體計數邏輯、開鎖行為控制等）
    │   └── interfaces.py # 💡 抽象介面定義（定義硬體高階行為，供基礎設施層繼承實作）
    │
    ├── infrastructure/   # 🔌【基礎設施層】完全解耦、隨插即用的實體驅動與工具
    │   ├── __init__.py
    │   ├── gpio/         # GPIO 控制獨立套件
    │   │   ├── __init__.py
    │   │   └── gpio_drivers.py # 實體 GPIO 輸出輸入驅動實作
    │   └── mqtt/         # MQTT 通訊獨立套件
    │       ├── __init__.py
    │       └── mqtt_client.py   # 實體 MQTT 客戶端發送與接收實作
    │
    ├── database/         # 💾【資料與儲存適配層】
    │   ├── __init__.py
    │   ├── connection.py # SQLite 資料庫連線初始化與連線池管理
    │   └── crud.py       # 定義資料增刪查改的通用 SQL 運作
    │
    └── tests/            # 🧪【獨立測試層】
        ├── __init__.py
        ├── conftest.py   # Pytest 全域配置（在此配置 Mock 硬體，使其可在 WSL 順利測試）
        └── test_core.py  # 針對核心硬體邏輯、狀態機的單元測試
```

## 📐 核心設計優勢
1. 極致輕量化：移除網頁伺服器（FastAPI / Uvicorn）的運算開銷，大幅降低記憶體與 CPU 佔用率，確保樹莓派能長期穩定運行背景監聽程式。
2. 引腳組態化：新增 app/config/gpio/gpio.cfg 後，實體硬體腳位完全被參數化。未來若因硬體電路板改版而變更樹莓派引腳，開發者只需修改此設定檔，完全不需要更動任何一行 Python 程式碼，實現極佳的維護性。