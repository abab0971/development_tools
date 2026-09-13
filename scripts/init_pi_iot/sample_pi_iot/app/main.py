# -*- coding: utf-8 -*-
# ==============================================================================
# File: main.py
# Brief: 系統唯一的啟動進入點（高度純淨之工業級組合根，負責多環境動態注入）
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 負責讀取設定、實體化硬體，並注入至核心管理器中運行
# ==============================================================================
import time
import sys
import os

from app.config import settings
from app.core.hardware import SmartCoreManager, CoreFsmParams
from app.infrastructure.logging.python_logger import PythonLogger
from app.common.persistence import AtomicFileStorage


def _bootstrap_dependencies(main_logger) -> dict:
    """
    判斷實體/模擬環境，實體化所有相依之硬體驅動與服務代理
    """
    is_mock_global = settings.MOCK_HARDWARE

    use_mock_gpio = is_mock_global or settings.MOCK_GPIO
    use_mock_ota = is_mock_global or settings.MOCK_OTA
    use_mock_webhook = is_mock_global or settings.MOCK_WEBHOOK

    if is_mock_global:
        main_logger.info("Running in PURE MOCK MODE (Global MOCK_HARDWARE=true)...")
    else:
        main_logger.info("Running in HYBRID/PRODUCTION MODE. Loading selective drivers...")

    deps = {}

    # TODO: 新建專案後，必須依據實際硬體需求，補充更多自檢邏輯，例如 GPIO 連線檢查、感測器初始化、鎖控狀態確認等，以取代下列範例程式碼
    # --- GPIO 驅動注入 ---
    if use_mock_gpio:
        from app.infrastructure.mock.mock_drivers import MockGpioOut, MockGpioIn

        deps["green_led"] = MockGpioOut(pin=settings.GREEN_LED_PIN, logger=main_logger)
        deps["red_led"] = MockGpioOut(pin=settings.RED_LED_PIN, logger=main_logger)
        deps["yellow_led"] = MockGpioOut(pin=settings.YELLOW_LED_PIN, logger=main_logger)
        deps["lock_ctrl"] = MockGpioOut(pin=settings.LOCK_CTRL_PIN, logger=main_logger)
        deps["lock_status"] = MockGpioIn(pin=settings.LOCK_STATUS_PIN, logger=main_logger)
    else:
        from app.infrastructure.gpio.gpio_driver import GPIO_OUT_Controller, GPIO_IN_Controller
        import RPi.GPIO as GPIO

        deps["green_led"] = GPIO_OUT_Controller(pin=settings.GREEN_LED_PIN, default_state=0)
        deps["red_led"] = GPIO_OUT_Controller(pin=settings.RED_LED_PIN, default_state=0)
        deps["yellow_led"] = GPIO_OUT_Controller(pin=settings.YELLOW_LED_PIN, default_state=0)
        deps["lock_ctrl"] = GPIO_OUT_Controller(pin=settings.LOCK_CTRL_PIN, default_state=1)
        deps["lock_status"] = GPIO_IN_Controller(pin=settings.LOCK_STATUS_PIN, mode=GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # --- OTA 代理注入 ---
    if use_mock_ota:
        from app.infrastructure.mock.mock_drivers import MockOtaAgent

        deps["ota_agent"] = MockOtaAgent(logger=main_logger)
    else:
        # from app.infrastructure.ota.downloader import TftpDownloader
        from app.infrastructure.ota.downloader import HttpDownloader
        from app.infrastructure.ota.ota_agent import OtaAgent

        # TFTP
        # tftp_ip = os.environ.get("TFTP_SERVER_IP", "192.168.1.100")
        # deps["ota_agent"] = OtaAgent(downloader=TftpDownloader(server_ip=tftp_ip, logger=main_logger), logger=main_logger)

        # HTTP
        deps["ota_agent"] = OtaAgent(downloader=HttpDownloader(base_url=settings.OTA_SERVER_URL, logger=main_logger), logger=main_logger)

    # --- Webhook 代理注入 ---
    if use_mock_webhook:
        from app.infrastructure.mock.mock_drivers import MockWebhookAgent

        deps["webhook_agent"] = MockWebhookAgent(logger=main_logger)
    else:
        from app.infrastructure.webhook.discord_client import DiscordWebhookClient

        deps["webhook_agent"] = DiscordWebhookClient(
            webhook_url=settings.DISCORD_WEBHOOK_URL,
            username=settings.DISCORD_USERNAME,
            timeout_sec=settings.DISCORD_TIMEOUT_SEC,
            logger=main_logger,
        )

    # --- 持久化工具注入 ---
    deps["storage"] = AtomicFileStorage(logger=main_logger)

    return deps


def main():
    manager = None
    is_mock = settings.MOCK_HARDWARE
    # 若在 WSL 模擬模式下，強制將實體寫檔關閉，保護開發機 SSD 壽命
    to_file_strategy = not is_mock and settings.TO_FILE

    # 1. 實體化結構化日誌器
    main_logger = PythonLogger(
        name="app.main",
        log_level_int=settings.LOG_LEVEL,
        log_file_path=settings.LOG_FILE_PATH,
        encoding=settings.FILE_ENCODING,
        to_console=settings.TO_CONSOLE,
        to_file=to_file_strategy,
        max_bytes=settings.MAX_BYTES,
        backup_count=settings.BACKUP_COUNT,
        log_format=settings.LOG_FORMAT,
        date_format=settings.DATE_FORMAT,
    )

    core_logger = PythonLogger(
        name="app.core.hardware",
        log_level_int=settings.LOG_LEVEL,
        log_file_path=settings.LOG_FILE_PATH,
        encoding=settings.FILE_ENCODING,
        to_console=settings.TO_CONSOLE,
        to_file=to_file_strategy,
        max_bytes=settings.MAX_BYTES,
        backup_count=settings.BACKUP_COUNT,
        log_format=settings.LOG_FORMAT,
        date_format=settings.DATE_FORMAT,
    )

    main_logger.info("========================================")
    main_logger.info("  IoT Core Secure Boot Handshake.       ")
    main_logger.info("========================================")
    main_logger.info(f"  App Version   : {settings.APP_VERSION}")
    main_logger.info(f"  HW Model      : {settings.HW_MODEL}")
    main_logger.info(f"  Device ID     : {settings.DEVICE_ID}")
    main_logger.info(f"  Compose File  : {settings.DOCKER_COMPOSE_FILE}")
    main_logger.info(f"  OTA Server    : {settings.OTA_SERVER_URL}")
    main_logger.info("========================================")

    # 🎯 【第一階段：宣告程式安全點火】
    # 只要 Python 基礎環境正常，即刻產生 .boot_ok 告知看門狗「程式已成功點火」
    BOOT_FILE = "/workspace/data/.boot_ok"
    try:
        os.makedirs(os.path.dirname(BOOT_FILE), exist_ok=True)
        with open(BOOT_FILE, "w", encoding="utf-8") as f:
            f.write("OK")
        main_logger.info(f"[BOOT HANDSHAKE] Generated ignite token at {BOOT_FILE}")
    except Exception as e:
        main_logger.warning(f"Failed to write boot token: {e}")

    try:
        # 雙層防爆網：若實體驅動出錯，改用 Mock 代理並引導狀態機進入死鎖，避免 Docker 直接 Crash
        try:
            hardware_deps = _bootstrap_dependencies(main_logger)
            manager_force_fail_trigger = False
        except Exception as hardware_init_error:
            main_logger.error(f"[FATAL HARDWARE ERROR] Driver layer mapping exploded: {hardware_init_error}")
            main_logger.error("Entering core hardware bypass for emergency watchdog signaling...")

            from app.infrastructure.mock.mock_drivers import MockGpioOut, MockGpioIn, MockOtaAgent, MockWebhookAgent

            hardware_deps = {
                "green_led": MockGpioOut(0, main_logger),
                "red_led": MockGpioOut(0, main_logger),
                "yellow_led": MockGpioOut(0, main_logger),
                "lock_ctrl": MockGpioOut(0, main_logger),
                "lock_status": MockGpioIn(0, main_logger),
                "ota_agent": MockOtaAgent(main_logger),
                "webhook_agent": MockWebhookAgent(main_logger),
                "storage": AtomicFileStorage(logger=main_logger),
            }
            # 物理強行覆蓋自檢結果，逼迫核心狀態機稍後進入閃紅燈死鎖，引導看門狗進行 A/B 回滾
            manager_force_fail_trigger = True

        main_logger.info("Injecting parameterized FSM arguments into manager...")

        # 自動推導 Pydantic 相容設定至 FSM 參數模型
        settings_dict = settings.model_dump() if hasattr(settings, "model_dump") else settings.dict()
        fsm_kwargs = {k.lower(): v for k, v in settings_dict.items() if k.lower() in CoreFsmParams.__annotations__}
        core_params = CoreFsmParams(**fsm_kwargs)

        # 依賴注入 (Dictionary Unpacking)
        manager = SmartCoreManager(logger=core_logger, params=core_params, **hardware_deps)

        # TODO: 新建專案後，必須依據實際硬體需求，補充更多自檢邏輯，例如 GPIO 連線檢查、感測器初始化、鎖控狀態確認等，以取代下列範例程式碼，使其能夠在硬體異常時進入死鎖模式，引導看門狗進行 A/B 回滾
        if manager_force_fail_trigger:
            # 欺騙大腦，讓其進入開機硬體健康檢查失敗的死鎖狀態，這樣看門狗等不到 .health_ok 就會啟動回滾！
            main_logger.error("Forcing core manager into Hardware Defect Deadlock.")
            manager.lock_status.read = lambda: 1  # 破壞自檢引導閃紅燈

        # 執行系統初始化自檢與遠端 OTA 版本檢查
        manager.system_init()

        # 🎯 【第二階段：寫入健全上線標記】
        # 百分之百通過硬體自檢且無 OTA 升級需求時，寫入 .health_ok 標記
        HEALTH_FILE = "/workspace/data/.health_ok"
        try:
            with open(HEALTH_FILE, "w", encoding="utf-8") as f:
                f.write("OK")
            main_logger.info(f"[HEALTH LOCK] Established baseline at {HEALTH_FILE}")
        except Exception as e:
            main_logger.warning(f"Failed to write health baseline: {e}")

        # 啟動主迴圈
        main_logger.info("System started successfully! Monitoring background cycles...")
        manager.is_running = True
        while manager.is_running:
            manager.run_cycle()
            time.sleep(settings.LOOP_MAIN_SLEEP_SEC)  # 休眠，防止 CPU 100% 滿載

    except KeyboardInterrupt:
        main_logger.warning("Keyboard interrupt detected (Ctrl+C). Preparing to shutdown...")
    except Exception as e:
        main_logger.error(f"Top-level unexpected crash: {e}")
    finally:
        # ==========================================
        # 安全清理與釋放硬體資源
        # ==========================================
        if manager:
            manager.system_cleanup()

        # GPIO 資源強制釋放 (判斷是否有匯入 RPi.GPIO)
        if "RPi.GPIO" in sys.modules:
            main_logger.info("Releasing physical GPIO resources...")
            try:
                import RPi.GPIO as GPIO

                GPIO.cleanup()
            except Exception:
                pass

        main_logger.info("System shutdown safely.")


if __name__ == "__main__":
    main()
