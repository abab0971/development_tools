# -*- coding: utf-8 -*-
# ==============================================================================
# File: downloader.py
# Brief: OTA 多協定下載器介面與 TFTP 實作 (Strategy Pattern)
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-05-31 04:13:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 定義一個抽象的檔案下載器介面 IFileDownloader 供 OTA Agent 動態注入使用，可擴展其他協定的下載器實作
# ==============================================================================

from abc import ABC, abstractmethod
import tftpy
import os
import urllib.request  # 🎯 內建 HTTP 請求庫
import urllib.error  # 🎯 HTTP 錯誤處理庫
from app.core.interfaces import ILogger


class IFileDownloader(ABC):
    """檔案下載器抽象策略介面"""

    @abstractmethod
    def download(self, remote_filename: str, local_filepath: str) -> bool:
        """下載遠端檔案至本地端，回傳是否成功"""
        pass


class TftpDownloader(IFileDownloader):
    """基於 TFTP 協定的下載器實作"""

    def __init__(self, server_ip: str, logger: ILogger, port: int = 69):
        self.server_ip = server_ip
        self.port = port
        self.logger = logger  # 🎯 綁定 logger

    def download(self, remote_filename: str, local_filepath: str) -> bool:
        try:
            # 確保本地目錄存在
            os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
            client = tftpy.TftpClient(self.server_ip, self.port)
            # tftpy 下載檔案，若有錯誤會拋出 Exception
            client.download(remote_filename, local_filepath)
            return True
        except Exception as e:
            # 🎯 錯誤訊息寫入日誌系統
            self.logger.error(f"[TFTP ERROR] Failed to download {remote_filename}: {e}")
            return False


# 🎯 實作 HTTP/HTTPS 下載器 (加入嚴格超時熔斷機制)
class HttpDownloader(IFileDownloader):
    """基於 HTTP/HTTPS 協定的下載器實作 (支援 TLS 加密與 NAT 穿透)"""

    def __init__(self, base_url: str, logger: ILogger, timeout_sec: int = 15):
        # 自動處理網址結尾的斜線
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.logger = logger
        # 🎯 設定嚴格的網路超時時間，必須遠小於 Watchdog 的 120 秒！
        self.timeout_sec = timeout_sec

    def download(self, remote_filename: str, local_filepath: str) -> bool:
        try:
            os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
            url = self.base_url + remote_filename
            self.logger.info(f"[HTTP DOWNLOAD] Fetching {url} (Timeout: {self.timeout_sec}s)...")

            # 🎯 修正：捨棄 urlretrieve，改用 urllib.request.urlopen 以強制賦予 Timeout 參數
            with urllib.request.urlopen(url, timeout=self.timeout_sec) as response:
                with open(local_filepath, "wb") as out_file:
                    out_file.write(response.read())

            return True
        except urllib.error.URLError as e:
            # e.reason 可能是 socket.timeout 或 [Errno 110]
            self.logger.error(f"[HTTP ERROR] Failed to download {remote_filename}: {e.reason}")
            return False
        except Exception as e:
            self.logger.error(f"[HTTP ERROR] Unexpected error downloading {remote_filename}: {e}")
            return False
