# 🌐 Raspberry Pi (IoT + Web Portal) 專案結構初始化工具

此工具用於一鍵生成完整的物聯網與**網頁監控整合後台 (Web Portal)** 專案。本樣板在乾淨架構的分層結構中，完整導入了 FastAPI 網頁服務、WebSocket 即時雙向通訊、Jinja2 後端網頁渲染與 Bootstrap 前端靜態資源，適合需要提供即時可視化儀表板 (Dashboard) 與網頁遠端控制的進階樹莓派應用專案。

---

## 📂 生成的專案結構說明

執行 `init_pi_web.sh` 後，將會自動生成以下全棧式的目錄與檔案結構。每個檔案皆已自動注入標準專案標頭（Head 註釋）：

```text
test_project/
├── .env                  # 環境變數設定檔（管理機密金鑰、主機 IP、資料庫路徑）
├── .gitignore            # Git 忽略清單（排除暫存檔與本地實體資料庫）
├── Dockerfile            # 跨平台 Docker 藍圖（多階段編譯，自適應 WSL 與樹莓派 ARM64）
├── docker-compose.yml    # 多容器編排（一鍵管理 Python App 與 Mosquitto MQTT Broker）
├── requirements.txt      # Python 核心套件依賴清單（FastAPI, Pydantic, smbus2 等）
├── README.md             # 專案部署說明文件
│
├── data/                 # 資料持久化目錄（由 Docker Volume 映射）
│   └── .gitkeep          # 確保空目錄能被 Git 追蹤
│
├── mosquitto/            # MQTT Broker 獨立設定檔目錄
│   └── config/
│       └── mosquitto.conf # Mosquitto 伺服器設定檔
│
└── app/                  # 應用程式原始碼主目錄
    ├── __init__.py       # 將 app 宣告為 Python 套件
    ├── main.py           # 應用程式唯一的啟動進入點（在此載入 FastAPI 與執行依賴注入）
    ├── config.py         # 全域設定模組（利用 Pydantic 載入與驗證 .env 環境變數）
    │
    ├── common/           # 🛠️【通用工具層】不涉及業務與硬體狀態的純工具函數
    │   ├── __init__.py
    │   └── utils.py      # 通用輔助函式與計算工具
    │
    ├── config/           # ⚙️【特定功能獨立設定檔目錄】
    │   └── gpio/
    │       └── gpio.cfg  # INI 格式的硬體引腳設定檔，將實體腳位與程式碼解耦
    │
    ├── core/             # 🔥【核心層】純粹的業務與硬體控制邏輯
    │   ├── __init__.py
    │   ├── hardware.py   # 狀態機與業務核心（定義如箱體開鎖、計數與燈號狀態控制）
    │   └── interfaces.py # 💡 抽象介面定義（定義通知服務與實體驅動的規範）
    │
    ├── infrastructure/   # 🔌【基礎設施層】完全解耦、隨插即用的實體驅動套件
    │   ├── __init__.py
    │   ├── gpio/         # GPIO 輸出輸入控制獨立套件
    │   │   ├── __init__.py
    │   │   └── gpio_drivers.py
    │   └── mqtt/         # MQTT 通訊獨立套件
    │       ├── __init__.py
    │       └── mqtt_client.py
    │
    ├── database/         # 💾【資料與儲存適配層】
    │   ├── __init__.py
    │   ├── connection.py # SQLite 資料庫連線初始化與連線池管理
    │   └── crud.py       # 定義資料增刪查改的通用 SQL 運作
    │
    ├── api/              # 🌐【外部傳輸層 - 網頁通訊接口】網頁與硬體之間的橋樑
    │   ├── __init__.py
    │   ├── v1/
    │   │   └── endpoints.py # HTTP RESTful API 接口（接收網頁按鈕指令並呼叫核心層）
    │   └── websocket.py  # WebSocket 傳輸接口（用於將感測器數據即時零延遲推送到網頁）
    │
    ├── static/           # 🎨【網頁前端靜態資源】
    │   ├── css/          # 存放 Bootstrap 等佈局樣式表
    │   │   └── .gitkeep  # 確保空目錄能被 Git 追蹤
    │   └── js/           # 存放前端 JavaScript（處理 WebSocket 接收、非同步 fetch 請求）
    │       └── .gitkeep  # 確保空目錄能被 Git 追蹤
    │
    ├── templates/        # 📄【後端網頁範本】
    │   └── index.html    # 控制儀表板網頁畫面（整合前端 UI 與遠端硬體控制按鈕）
    │
    └── tests/            # 🧪【獨立測試層】
        ├── __init__.py
        ├── conftest.py   # Pytest 全域配置（配置 Mock 硬體）
        ├── test_api.py   # 針對 FastAPI 路由與通訊接口的單元測試
        └── test_core.py  # 針對核心硬體邏輯的單元測試
```

## 網頁與硬體同步的核心機制
1. 即時數據推播 (WebSocket)：當實體樹莓派感測器觸發或計數變更時，api/websocket.py 會自動將數據推送到前端 static/js/，前端網頁免重新整理即可實時更新畫面。
2. 非同步遠端控制 (REST API)：當使用者在網頁儀表板上點擊控制按鈕，前端 JS 會發送 HTTP 請求至 api/v1/endpoints.py，該層接收後立刻指揮 core/hardware.py 驅動實體繼電器或電子鎖。