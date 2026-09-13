# -*- coding: utf-8 -*-
# ==============================================================================
# File: interfaces.py
# Brief: 核心層硬體驅動與外部通知服務之抽象介面定義
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 核心層只依賴這些介面，不依賴具體的 infrastructure 實作
# ==============================================================================

from abc import ABC, abstractmethod
from enum import IntEnum


# ==========================================
# 通用工控語意狀態枚舉 (Enums)
# ==========================================
class PinState(IntEnum):
    LOW = 0
    HIGH = 1


class LockCtrl(IntEnum):
    UNLOCK = 1
    LOCK = 0


class GateStatus(IntEnum):
    CLOSED = 0
    OPEN = 1


class ILogger(ABC):
    """
    工業級日誌抽象介面合約。
    確保核心業務大腦不與任何實體寫檔套件或作業系統 I/O 強綁定。
    """

    @abstractmethod
    def debug(self, msg: str) -> None:
        pass

    @abstractmethod
    def info(self, msg: str) -> None:
        pass

    @abstractmethod
    def warning(self, msg: str) -> None:
        pass

    @abstractmethod
    def error(self, msg: str) -> None:
        pass


class IGpioOut(ABC):
    @abstractmethod
    def write(self, value: int) -> None:
        """寫入數位高低電平訊號 (1 或 0)"""
        pass


class IGpioIn(ABC):
    @abstractmethod
    def read(self) -> int:
        """讀取數位高低電平訊號狀態 (1 或 0)"""
        pass


class IOtaAgent(ABC):
    """
    OTA 升級代理抽象介面。
    確保核心業務大腦不依賴特定的下載協定 (TFTP/HTTP) 或實體檔案操作。
    """

    @abstractmethod
    def check_for_updates(self) -> bool:
        """
        執行版本檢查與下載驗證。
        回傳 True 代表有新版本且已驗證下載成功，系統應準備優雅停機。
        """
        pass


class IWebhookAgent(ABC):
    """
    通用 Webhook 通知代理抽象介面。
    """

    @abstractmethod
    def send_message(self, message: str) -> bool:
        """
        傳送文字訊息至設定之 Webhook 遠端端點。
        :param message: 格式化文字字串
        :return: 傳送成功回傳 True，否則回傳 False
        """
        pass
