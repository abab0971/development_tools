# development_tools
開發用工具

# 🛠️ Development Tools (開發工具箱)

這是一個專為 WSL Ubuntu 環境開發的輕量化自動化工具箱，旨在簡化樹莓派 (Raspberry Pi 5 / Zero 2W) 與 FastAPI 物聯網專案的初始化與日常開發流程。

## 📋 功能特點
* **一鍵生成 Clean Architecture 專案**：自動建立解耦的 Python 乾淨架構目錄。
* **支援靈活路徑**：可自由指定絕對路徑或相對路徑來生成專案。
* **標準 CLI 參數支援**：具備 `-h` (說明) 與 `-v` (版本) 選項。
* **環境友善**：終端機互動與輸出全面英文語系化，防止 Docker 或純 SSH 遠端環境亂碼。

---

## 🚀 快速開始

### 1. 賦予執行權限
在首次使用前，請確保腳本具備可執行權限：
```bash
chmod +x manage.sh scripts/init_project.sh
```

### 2. 使用方式

#### 💡 A. 啟動互動式選單 (Interactive Menu)
直接執行腳本即可進入主選單：
```bash
./manage.sh
```
* 進入選單後輸入 1，即可開始初始化專案。
* 可直接按 Enter 使用目前目錄，或輸入如 ../my_iot_project 建立新資料夾。

#### 💡 B. 查看幫助訊息 (Help)
```bash
./manage.sh -h
```
或
```bash
./manage.sh --help
```

#### 💡 C. 查看版本號 (Version)
```bash
./manage.sh -v
```
或
```bash
./manage.sh --version
```

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
chmod +x manage.sh scripts/init_pi_project/init_pi_project.sh