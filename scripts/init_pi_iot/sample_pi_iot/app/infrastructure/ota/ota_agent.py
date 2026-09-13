# -*- coding: utf-8 -*-
# ==============================================================================
# File: ota_agent.py
# Brief: OTA 升級代理大腦 (負責 Manifest 解析、防偽驗證與交接標記)
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-05-31 04:16:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 負責解析從 TFTP 下載的 ota_manifest.json，驗證版本血統與檔案完整性，並在成功後寫入交接標記給 Watchdog 以觸發重啟流程
# ==============================================================================

import json
import hashlib
import os
from typing import Optional
from app.infrastructure.ota.downloader import IFileDownloader
from app.core.interfaces import ILogger


class OtaAgent:
    def __init__(
        self,
        downloader: IFileDownloader,
        logger: ILogger,  # 🎯 接收 logger
        local_version_path: str = "/workspace/version.json",
        data_dir: str = "/workspace/data",
    ):
        self.downloader = downloader
        self.logger = logger  # 🎯 綁定 logger
        self.local_version_path = local_version_path
        self.data_dir = data_dir
        self.cache_dir = os.path.join(data_dir, "ota_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _calculate_sha256(self, filepath: str) -> str:
        """計算實體檔案的 SHA256 防偽驗證碼"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def check_for_updates(self) -> bool:
        """
        執行完整的 OTA 檢查、下載與驗證流程。
        回傳 True 代表「下載且驗證成功，請求大腦準備停機」。
        """
        manifest_local = os.path.join(self.cache_dir, "ota_manifest.json")
        update_tar_local = os.path.join(self.cache_dir, "update.tar.gz")

        # 🎯 定義黑名單與嘗試紀錄檔的路徑
        blacklist_path = os.path.join(self.data_dir, "ota_blacklist.txt")
        attempt_path = os.path.join(self.data_dir, ".ota_attempt")

        self.logger.info("[OTA] Checking for updates...")
        # 1. 嘗試下載最新的 ota_manifest.json
        if not self.downloader.download("ota_manifest.json", manifest_local):
            self.logger.warning("[OTA] No new manifest found or download failed.")
            return False

        # 2. 解析遠端宣告與本地版本
        try:
            with open(manifest_local, "r") as f:
                remote_manifest = json.load(f)
            with open(self.local_version_path, "r") as f:
                local_version = json.load(f)
        except Exception as e:
            self.logger.error(f"[OTA ERROR] Failed to parse JSON: {e}")
            return False

        # 3. 嚴格的血統防護 (防止刷錯專案或分支)
        if remote_manifest["project_name"] != local_version["project_name"]:
            self.logger.error("[OTA REJECTED] Project name mismatch!")
            return False
        if remote_manifest["flavor"] != local_version["flavor"]:
            self.logger.error("[OTA REJECTED] Firmware flavor mismatch!")
            return False

        # 4. 版本比較
        if remote_manifest.get("version") == local_version.get("version"):
            self.logger.info(f"[OTA] Current version {remote_manifest.get('version')} matches remote server.")
            # 🎯 修正：只要版號一致，且本地 build_date 不為空的預設開發字串，就直接判定無須更新
            # 這樣可以徹底杜絕回滾後，因為任何原因導致的重複下載
            if remote_manifest.get("release_time") == local_version.get("build_date") or local_version.get("build_date") == "DEV_LOCAL":
                self.logger.info("[OTA] Hardware baseline and Build date matched. Skip update.")
                return False

            self.logger.info("[OTA] Higher Build Date detected on server. Proceeding to flashing...")

        # 🛡️ 【新增：黑名單防禦機制】
        # 在決定下載前，先檢查這個韌體的 Hash 是否已經害我們當機過
        if os.path.exists(blacklist_path):
            try:
                with open(blacklist_path, "r") as f:
                    blacklisted_hashes = [line.strip() for line in f.readlines()]
                if remote_manifest["firmware_hash"] in blacklisted_hashes:
                    self.logger.error(f"[OTA REJECTED] Firmware {remote_manifest['version']} is BLACKLISTED due to previous boot failure!")
                    self.logger.error("Skipping update to prevent infinite crash loop.")
                    return False
            except Exception as e:
                self.logger.warning(f"Failed to read blacklist: {e}")

        self.logger.info(f"[OTA] New version detected: {remote_manifest['version']}. Downloading firmware...")

        # 5. 下載實體更新包
        if not self.downloader.download("update.tar.gz", update_tar_local):
            self.logger.error("[OTA ERROR] Firmware payload download failed.")
            return False

        # 6. 🛡️ 拆解防偽封條 (SHA256 完整性驗證)
        self.logger.info("[OTA] Verifying firmware integrity (SHA256)...")
        calculated_hash = self._calculate_sha256(update_tar_local)

        if calculated_hash != remote_manifest["firmware_hash"]:
            self.logger.error(f"[OTA CRITICAL] Hash mismatch! File corrupted or tampered.")
            self.logger.error(f"Expected: {remote_manifest['firmware_hash']}")
            self.logger.error(f"Got:      {calculated_hash}")
            os.remove(update_tar_local)
            return False

        self.logger.info("[OTA SUCCESS] Firmware verified successfully!")

        # 📝 【新增：留下嘗試紀錄】
        # 把這包韌體的 Hash 記下來，如果等一下重啟失敗，看門狗就會把它抓進黑名單
        try:
            with open(attempt_path, "w") as f:
                f.write(remote_manifest["firmware_hash"])
        except Exception as e:
            self.logger.warning(f"Failed to write OTA attempt flag: {e}")

        # 7. 寫入交接標記給外層 Watchdog
        ready_flag = os.path.join(self.data_dir, ".ota_ready")
        with open(ready_flag, "w") as f:
            f.write("READY_FOR_REBOOT")

        return True
