# -*- coding: utf-8 -*-
# ==============================================================================
# File: mock_drivers.py
# Brief: 模擬基礎設施層 —— WSL/PC 開發專用之虛擬硬體驅動實作
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 本套件提供核心業務邏輯的模擬硬體實作，供測試與開發使用
# ==============================================================================
from app.core.interfaces import (
    IGpioOut,
    IGpioIn,
    ILogger,
    IOtaAgent,
    IWebhookAgent,
)


class MockGpioOut(IGpioOut):
    def __init__(self, pin: int, logger: ILogger):
        self.pin = pin
        self.logger = logger

    def write(self, value: int) -> None:
        self.logger.info(f"[MOCK GPIO OUT] Pin [{self.pin}] set to -> {value}")


class MockGpioIn(IGpioIn):
    def __init__(self, pin: int, logger: ILogger):
        self.pin = pin
        self.logger = logger

    def read(self) -> int:
        self.logger.debug(f"[MOCK GPIO IN] Reading Pin [{self.pin}] -> Returning default 0 (CLOSED)")
        return 0


class MockOtaAgent(IOtaAgent):
    def __init__(self, logger: ILogger):
        self.logger = logger

    def check_for_updates(self) -> bool:
        self.logger.info("[MOCK OTA] Checking for updates... Forced to return False.")
        return False


class MockWebhookAgent(IWebhookAgent):
    """
    WSL / PC 開發測試環境專用之 Webhook 虛擬模擬器
    """

    def __init__(self, logger: ILogger):
        self.logger = logger

    def send_message(self, message: str) -> bool:
        self.logger.info("[MOCK WEBHOOK] Intercepted notification dispatch stream:")
        self.logger.info("------------------------------------------------------------")
        for line in message.split("\n"):
            self.logger.info(f"    {line}")
        self.logger.info("------------------------------------------------------------")
        self.logger.info("[MOCK WEBHOOK SUCCESS] Simulated HTTP 204 No Content return.")
        return True
