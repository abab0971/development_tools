# -*- coding: utf-8 -*-
# ==============================================================================
# File: persistence.py
# Brief: 具備原子性 (Atomic) 與磁碟強制沖刷 (fsync) 的簡單檔案讀寫模組
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-08-16 17:25:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice:
# ==============================================================================
import os
from app.core.interfaces import ILogger


class AtomicFileStorage:
    """
    通用檔案存取控制器，使用寫入 .tmp + fsync + os.replace 確保斷電寫入安全
    """

    def __init__(self, logger: ILogger):
        self.logger = logger

    def atomic_write(self, filepath: str, content: str) -> bool:
        """原子寫入純文字，防範斷電造成 0 Byte 破損"""
        tmp_file = f"{filepath}.tmp"
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(tmp_file, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())  # 強制沖刷實體寫入磁碟
            os.replace(tmp_file, filepath)  # 原子替換
            return True
        except Exception as e:
            self.logger.error(f"[STORAGE ERROR] Failed to write atomic file ({filepath}): {e}")
            if os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except Exception:
                    pass
            return False

    def read_text(self, filepath: str, default: str = "") -> str:
        """讀取檔案文字內容，檔案不存在或異常時傳回預設值"""
        if not os.path.exists(filepath):
            return default
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            self.logger.warning(f"[STORAGE WARN] Read failed ({filepath}), fallback to default: {e}")
            return default

    def append_line(self, filepath: str, line_content: str) -> bool:
        """向歷史日誌追加單行文字"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(f"{line_content}\n")
                f.flush()
                os.fsync(f.fileno())
            return True
        except Exception as e:
            self.logger.error(f"[STORAGE ERROR] Append history failed ({filepath}): {e}")
            return False
