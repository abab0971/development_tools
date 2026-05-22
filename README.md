# 🛠️ Development Tools (開發工具箱)

這是一個專為 WSL Ubuntu 環境開發的輕量化自動化工具箱，旨在簡化樹莓派 (Raspberry Pi 5 / Zero 2W) 與 FastAPI 物聯網專案的初始化與日常開發流程。

## 📋 功能特點
1. **🚀 Initialize Pi (IoT Core) Project**：一鍵生成純硬體控制與通訊核心專案。不包含網頁路由與靜態檔案，`common/` 僅保留 `utils.py`，`infrastructure/` 僅保留 `gpio` 與 `mqtt` 獨立模組包。
2. **🌐 Initialize Pi (IoT + Web Portal) Project**：一鍵生成帶有網頁控制台的完整專案架構（包含 FastAPI 介面、WebSocket、Jinja2 網頁範本與前端靜態資源）。
3. **📦 Generate Customized Module Block**：在任意指定路徑建立高重用性的子模組，自動生成包含標準專案 Head 註釋的 `__init__.py` 與 `main.py`。

---

## 🚀 快速開始

### 1. 賦予執行權限
在首次使用前，請確保腳本具備可執行權限：
```bash
chmod +x manage.sh scripts/*/*.sh
```

### 2. 使用方式

#### 💡 A. 啟動互動式選單 (Interactive Menu)
直接執行腳本即可進入主選單：
```bash
./manage.sh
```
* 進入選單後輸入 1，即可開始初始化專案。
* 可直接按 Enter 使用目前目錄，或輸入如 ../my_iot_project 建立新資料夾。

#### 💡 B. 標準參數支援
* 查看幫助：`./manage.sh -h` 或 `./manage.sh --help`
* 查看版本：`./manage.sh -v` 或 `./manage.sh --version`


---
## 📂 工具箱架構

```bash
development_tools/
├── README.txt           # 本說明文件 (純文字版)
├── manage.sh            # 主進入點 (CLI 管理核心)
└── scripts/             # 子功能腳本存放區
    └── init_project.sh  # 專案目錄結構生成器
```

---
## 🔄 未來擴充

```
本工具箱採用模組化設計。未來若有自動化部署 (Deploy)、資料庫備份 (Backup) 
或日誌清理 (Log Clean) 的需求，只需在 scripts/ 建立新腳本，並於 
manage.sh 的 case 選單中加入對應選項即可。
```

---

## ⚙️ 權限檢查確認

程式碼更新完成後，請記得在 WSL 中執行以下指令，確保新加入的機制與檔案權限都正確：

```bash
chmod +x manage.sh scripts/*/*.sh
```