# -*- coding: utf-8 -*-
# ==============================================================================
# File: hardware.py
# Brief: 實體硬體有限狀態機 (FSM) 與高安全性業務邏輯核心實作
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 本層僅透過介面控制硬體
# ==============================================================================

import sys
import time
from dataclasses import dataclass
from app.core.interfaces import (
    IGpioOut,
    IGpioIn,
    IWebhookAgent,
    ILogger,
    PinState,
    LockCtrl,
    GateStatus,
    IOtaAgent,
)
from app.common.persistence import AtomicFileStorage


# 核心狀態機參數物件化宣告
@dataclass
class CoreFsmParams:
    loop_main_sleep_sec: float
    device_id: str
    app_version: str
    # TODO: 若有需要，這裡可以加入更多的初始化邏輯，例如讀取持久化計數資料、恢復上次狀態等
    # counter_file_path: str
    webhook_enabled: bool


class SmartCoreManager:
    """
    通用樹莓派 IoT 核心業務邏輯管理器。
    採用依賴注入 (Dependency Injection) 接收所有硬體驅動與網路服務代理實體。
    """

    def __init__(
        self,
        green_led: IGpioOut,
        red_led: IGpioOut,
        yellow_led: IGpioOut,
        lock_ctrl: IGpioOut,
        lock_status: IGpioIn,
        storage: AtomicFileStorage,
        webhook_agent: IWebhookAgent,
        params: CoreFsmParams,
        logger: ILogger,
        ota_agent: IOtaAgent = None,
    ):
        # 1. 注入基礎設施與硬體驅動介面
        self.green_led = green_led
        self.red_led = red_led
        self.yellow_led = yellow_led
        self.lock_ctrl = lock_ctrl
        self.lock_status = lock_status
        self.storage = storage
        self.webhook_agent = webhook_agent

        # 2. 注入參數與狀態變數
        self.params = params
        self.logger = logger
        self.ota_agent = ota_agent

        self.counting = 0
        self.is_running = False

    # 指示燈控制封裝方法
    def _set_leds(self, green: PinState, yellow: PinState, red: PinState) -> None:
        """統一控制指示燈狀態"""
        self.green_led.write(green.value)
        self.yellow_led.write(yellow.value)
        self.red_led.write(red.value)

    def _send_webhook_alert(self, message: str) -> None:
        """檢查 Webhook 開關，若啟用則非阻塞發送通知"""
        if self.params.webhook_enabled and self.webhook_agent:
            self.webhook_agent.send_message(message)

    def system_init(self) -> None:
        """開機硬體健康連鎖自檢與初始化流程"""
        self.logger.info("Initializing system hardware baseline...")

        # ======================================================================
        # 🛡️ 1. 硬體健康度與系統時鐘自檢 (Hardware Self-test)
        # ======================================================================
        hardware_ok = True
        error_reasons = []

        try:
            # NTP 校時防線：檢查系統時間年份是否已校正 (須 >= 2026)
            current_year = int(time.strftime("%Y", time.localtime()))
            if current_year < 2026:
                hardware_ok = False
                error_reasons.append(f"System clock invalid ({current_year} < 2026, NTP not synced).")
                self.logger.error(f"[NTP ERROR] System clock year is {current_year}. Refusing to start.")

            # TODO: 新建專案後，必須依據實際硬體需求，補充更多自檢邏輯，例如 GPIO 連線檢查、感測器初始化、鎖控狀態確認等，以取代下列範例程式碼
            # 檢查閘門或初始機構電平狀態(不檢查，基本專案不會有這個需求)
            # if self.lock_status.read() != GateStatus.CLOSED.value:
            #     hardware_ok = False
            #     error_reasons.append("Initial gate/sensor position not in CLOSED state.")

        except Exception as e:
            # 捕捉任何物理斷線或暫存器讀寫異常
            hardware_ok = False
            error_reasons.append(f"Exception during component setup: {e}")

        # ======================================================================
        # 🛑 2. 故障警示與死鎖模式 (開機自檢失敗時進入，引導看門狗進行 A/B 槽回滾)
        # ======================================================================
        if not hardware_ok:
            self.logger.error(f"System boot FAILED due to hardware errors: {error_reasons}")
            self.logger.error("Entering emergency halt mode (Red LED flashing)...")
            # 發送致命故障 Webhook 通知
            reasons_str = ", ".join(error_reasons)
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            msg = f"Record Time: {now_time}\n" f"Device ID: {self.params.device_id}\n" f"Alert: 🚨 [Fatal Hardware Error] Boot self-test failed ({reasons_str})!"
            self._send_webhook_alert(msg)

            # 進入死鎖閃燈迴圈，阻斷 .health_ok 標記產生，讓外層 Watchdog 啟動安全回滾
            while True:
                self._set_leds(PinState.LOW, PinState.LOW, PinState.HIGH)
                time.sleep(0.5)
                self._set_leds(PinState.LOW, PinState.LOW, PinState.LOW)
                time.sleep(0.5)

        self.logger.info("Hardware self-test PASSED.")

        # ======================================================================
        # ✅ 3. 開機燈號跑馬燈回饋 (綠 -> 黃 -> 紅)
        # ======================================================================
        self.logger.info("Executing Boot LED Success sequence...")
        for _ in range(2):
            self._set_leds(PinState.HIGH, PinState.LOW, PinState.LOW)
            time.sleep(0.5)
            self._set_leds(PinState.LOW, PinState.HIGH, PinState.LOW)
            time.sleep(0.5)
            self._set_leds(PinState.LOW, PinState.LOW, PinState.HIGH)
            time.sleep(0.5)

        # ======================================================================
        # ⚙️ 4. 設定預設控制狀態與安全歸位
        # ======================================================================
        self.logger.info("Setting system default states...")
        self.lock_ctrl.write(LockCtrl.LOCK.value)
        self._set_leds(PinState.LOW, PinState.LOW, PinState.LOW)

        # ======================================================================
        # 5. 開機遠端 OTA 升級檢查
        # ======================================================================
        self.logger.info("Hardware self-test complete. Checking for OTA updates...")
        if self.ota_agent and self.ota_agent.check_for_updates():
            self.logger.warning("OTA Update verified! Initiating SYSTEM_UPDATING safe shutdown...")
            self._set_leds(PinState.HIGH, PinState.HIGH, PinState.LOW)
            self.logger.warning("Handing over control to Host Watchdog. Exiting gracefully...")
            sys.exit(0)

        # TODO: 若有需要，這裡可以加入更多的初始化邏輯，例如讀取持久化計數資料、恢復上次狀態等
        # 載入持久化計數資料
        # stored_count = self.storage.read_text(self.params.counter_file_path, default="0")
        # try:
        #     self.counting = int(stored_count)
        #     self.logger.info(f"[STORAGE] Restored counter value: {self.counting}")
        # except ValueError:
        #     self.counting = 0
        #     self.logger.warning("[STORAGE WARN] Corrupted counter file, reset to 0.")
        #     self.storage.atomic_write(self.params.counter_file_path, "0")

        self.logger.info("System initialization complete. Entering Smart Standby loop.")

    def system_cleanup(self) -> None:
        """系統關閉安全清理與資源釋放"""
        self.logger.info("System shutting down. Securely locking device...")
        self.lock_ctrl.write(LockCtrl.LOCK.value)
        self._set_leds(PinState.LOW, PinState.LOW, PinState.LOW)

    def run_cycle(self) -> None:
        """主迴圈單次執行邏輯（供外部 main 迴圈持續呼叫）"""
        # 保持燈號綠燈待機狀態
        self._set_leds(PinState.HIGH, PinState.LOW, PinState.LOW)
