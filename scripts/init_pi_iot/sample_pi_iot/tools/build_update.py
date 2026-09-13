#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# File: build_update.py
# Brief: 開發者工具 - 產出 OTA 升級包與 SHA256 防偽驗證碼 (動態注入)
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 1. 會從專案根目錄讀取 version.json 模板，注入動態資料後打包成 update.tar.gz
#         2. 需在專案根目錄下執行此腳本，並確保 git 環境可用以獲取 commit hash
# ==============================================================================

import os
import tarfile
import hashlib
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
    excludes = [
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        ".idea",
        ".vscode",
        "data",
        ".env",
        "tools",
        "output",
        "docs",
        "install.tar.gz",
        "update.tar.gz",
    ]
    # 攔截實體檔案
    if tarinfo.name.endswith("version.json"):
        return None

    for ext in excludes:
        if ext in tarinfo.name:
            return None
    return tarinfo


def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main():
    print("[OTA BUILD] Generating OTA Update Package...")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 建立 output 目錄
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)

    # 將輸出路徑指向 output 目錄
    output_tar = os.path.join(output_dir, "update.tar.gz")
    manifest_out = os.path.join(output_dir, "ota_manifest.json")

    # 1. 讀取並動態修改 Version 資料
    version_file = os.path.join(project_root, "version.json")
    with open(version_file, "r") as f:
        v_data = json.load(f)

    v_data["commit_hash"] = get_git_hash()
    v_data["build_date"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    v_bytes = json.dumps(v_data, indent=4).encode("utf-8")

    # 2. 打包壓縮檔與注入
    with tarfile.open(output_tar, "w:gz") as tar:
        tar.add(project_root, arcname=".", filter=filter_excludes)

        # OTA 包是解壓到當前目錄，所以 arcname 為 version.json
        info = tarfile.TarInfo(name="version.json")
        info.size = len(v_bytes)
        info.mtime = int(time.time())
        tar.addfile(tarinfo=info, fileobj=io.BytesIO(v_bytes))

    # 3. 計算檢查碼
    firmware_hash = calculate_sha256(output_tar)

    # 4. 產出外部 Manifest (對齊動態資料)
    manifest_data = {
        "project_name": v_data["project_name"],
        "flavor": v_data["flavor"],
        "version": v_data["version"],
        "commit_hash": v_data["commit_hash"],
        "firmware_hash": firmware_hash,
        "release_time": v_data["build_date"],
        "download_url": "https://<YOUR_OTA_SERVER>/update.tar.gz",
    }

    with open(manifest_out, "w") as f:
        json.dump(manifest_data, f, indent=4)

    print(f"[SUCCESS] OTA Package generated: {output_tar}")
    print(f"[SUCCESS] Git Hash: {v_data['commit_hash']}")
    print(f"[SUCCESS] SHA256 Checksum: {firmware_hash}")


if __name__ == "__main__":
    main()
