# -*- coding: utf-8 -*-
# ==============================================================================
# File: python_logger.py
# Brief: 基於 Python logging 標準庫之實體日誌驅動（相容 ISO 8601 UTC 與滾動熔斷）
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# ==============================================================================
import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.interfaces import ILogger


class PythonLogger(ILogger):
    """
    實體日誌控制器，繼承並實作內層 ILogger 合約。
    """

    def __init__(
        self,
        name: str,
        log_level_int: int,
        log_file_path: str,
        encoding: str,
        to_console: bool,
        to_file: bool,
        max_bytes: int,
        backup_count: int,
        log_format: str,
        date_format: str,
    ):
        self.logger = logging.getLogger(name)

        # 算術級別過濾映射 (4=DEBUG, 3=INFO, 2=WARNING, 1=ERROR)
        level_map = {
            4: logging.DEBUG,
            3: logging.INFO,
            2: logging.WARNING,
            1: logging.ERROR,
        }
        target_level = level_map.get(log_level_int, logging.INFO)
        self.logger.setLevel(target_level)

        # 防範重複註冊 Handler
        if not self.logger.handlers:
            formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

            # Stream A: Console 控制台輸出
            if to_console:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)

            # Stream B: 磁碟容量滾動 File 輸出
            if to_file:
                log_dir = os.path.dirname(log_file_path)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)

                file_handler = RotatingFileHandler(
                    log_file_path,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding=encoding,
                )
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)
