# 📦 自訂模組區塊生成工具 (Customized Module Block Generator)

此工具是一個輔助型的腳本，用於在開發過程中，隨時在指定的專案路徑下快速生成符合規範、高度重用性的 Python 獨立模組區塊（Sub-module Block）。工具會自動建立模組目錄，並生成預建**標準專案標頭 (Project Head 註釋)** 的 `__init__.py` 與 `main.py`。

---

## 📂 生成的模組結構

當您透過工具箱輸入特定的路徑與模組名稱（例如：在 `./app/infrastructure` 生成 `barcode_scanner`）後，該路徑下將自動產出：

```text
<指定路徑>/<自訂模組名稱>/
├── __init__.py        # 宣告為 Python 套件，包含標準標頭註釋
└── main.py            # 模組的主要實作或本地測試進入點，包含標準標頭註釋
```

## 自動產出的標準標頭範本 (Standard Head Block)
為了符合軟體工程的程式碼規範，產出的檔案頂部會自動注入以下結構的註釋。其中「建立者」會自動標註為 development_tools，「功能敘述」則特意留空，以便開發者後續填寫具體的硬體或功能說明：
```python
# -*- coding: utf-8 -*-
"""
File: main.py
Description: 
Creator: development_tools
Created Time: 2026-05-23 03:46:01
"""
```

## 使用場景與優勢
* 快速擴充硬體驅動：當您的回收箱專案需要臨時追加一個新硬體（例如 weight_sensor 重量感測器）時，只需選擇此選項，即可在 app/infrastructure/ 底下一鍵生成乾淨、標準化的套件骨架。
* 團隊規範一致性：自動帶入建立時間與檔案名稱，確保專案中的每一段原始碼都具備相同的標頭格式，提升程式碼審查 (Code Review) 與長期維護的品質。