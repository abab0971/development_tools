#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# File: build_install.py
# Brief: 開發者工具 - 產出乾淨的出廠安裝包 (動態注入 Git Hash 與 Build Date)
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 1. 會從專案根目錄讀取 version.json 模板，注入動態資料後打包成 install.tar.gz
#         2. 需在專案根目錄下執行此腳本，並確保 git 環境可用以獲取 commit hash
# ==============================================================================

import os
import tarfile
import json
import time
import io
import subprocess
from datetime import datetime


def get_git_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip()
    except Exception:
        return "UNKNOWN_HASH"


def filter_excludes(tarinfo):
    """過濾掉不需要的暫存檔，並攔截實體的 version.json"""
    excludes = [
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        ".idea",
        ".vscode",
        "data",
        ".env",
        "output",
        "docs",
        "install.tar.gz",
        "update.tar.gz",
    ]
    # 攔截實體檔案，我們等一下會在記憶體中手動注入
    if tarinfo.name.endswith("version.json"):
        return None

    for ext in excludes:
        if ext in tarinfo.name:
            return None
    return tarinfo


def main():
    print("[BUILD] Starting factory installation package build...")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 建立 output 目錄
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)

    # 將輸出路徑指向 output 目錄
    output_filename = os.path.join(output_dir, "install.tar.gz")

    # 1. 讀取並動態修改 Version 資料
    version_file = os.path.join(project_root, "version.json")
    with open(version_file, "r") as f:
        v_data = json.load(f)

    v_data["commit_hash"] = get_git_hash()
    v_data["build_date"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[INFO] Injecting Dynamic Meta: {v_data['commit_hash']} at {v_data['build_date']}")

    # 2. 轉為 bytes 以備記憶體注入
    v_bytes = json.dumps(v_data, indent=4).encode("utf-8")

    with tarfile.open(output_filename, "w:gz") as tar:
        # 打包實體檔案 (filter 會排除掉實體的 version.json)
        tar.add(project_root, arcname="__PROJ_NAME_UPPER__", filter=filter_excludes)

        # 3. 從記憶體中將注入好真實資料的 version.json 塞進壓縮檔
        info = tarfile.TarInfo(name="__PROJ_NAME_UPPER__/version.json")
        info.size = len(v_bytes)
        info.mtime = int(time.time())
        tar.addfile(tarinfo=info, fileobj=io.BytesIO(v_bytes))

    print(f"[SUCCESS] Factory package generated: {output_filename}")


if __name__ == "__main__":
    main()
