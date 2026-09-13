# -*- coding: utf-8 -*-
# ==============================================================================
# File: config.py
# Brief: 系統全域設定模組，負責載入與強制驗證設定檔
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice:
# ==============================================================================
import os
import sys
import json
import configparser
from pydantic import field_validator
from pydantic_settings import BaseSettings

# 1. 基礎路徑設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 【核心優化：通用設定檔註冊表】
CONFIG_REGISTRY = [
    {
        "path": os.path.join(BASE_DIR, "config", "logging", "logging.cfg"),
        "section": "LOGGING_CONFIG",
    },
    {
        "path": os.path.join(BASE_DIR, "config", "core", "core.cfg"),
        "section": "CORE_CONFIG",
    },
    {
        "path": os.path.join(BASE_DIR, "config", "gpio", "gpio.cfg"),
        "section": "PIN_MAPPING",
    },
    {
        "path": os.path.join(BASE_DIR, "config", "mock", "mock.cfg"),
        "section": "MOCK_CONFIG",
    },
    {
        "path": os.path.join(BASE_DIR, "config", "storage", "storage.cfg"),
        "section": "STORAGE_CONFIG",
    },
    {
        "path": os.path.join(BASE_DIR, "config", "webhook", "discord.cfg"),
        "section": "DISCORD_CONFIG",
    },
]


class Settings(BaseSettings):
    # config/logging/logging.cfg [LOGGING_CONFIG]
    LOG_LEVEL: int
    LOG_FILE_PATH: str
    FILE_ENCODING: str
    TO_CONSOLE: bool
    TO_FILE: bool
    MAX_BYTES: int
    BACKUP_COUNT: int
    LOG_FORMAT: str
    DATE_FORMAT: str

    # config/core/core.cfg [CORE_CONFIG]
    LOOP_MAIN_SLEEP_SEC: float

    # config/gpio/gpio.cfg [PIN_MAPPING]
    GREEN_LED_PIN: int
    RED_LED_PIN: int
    YELLOW_LED_PIN: int
    LOCK_CTRL_PIN: int
    LOCK_STATUS_PIN: int

    # config/mock/mock.cfg [MOCK_CONFIG]
    MOCK_GPIO: bool
    MOCK_OTA: bool
    MOCK_WEBHOOK: bool
    MOCK_MQTT: bool

    # TODO: 若有需要，這裡可以加入更多的初始化邏輯，例如讀取持久化計數資料、恢復上次狀態等
    # config/storage/storage.cfg [STORAGE_CONFIG]
    # COUNTER_FILE_PATH: str

    # config/webhook/discord.cfg [DISCORD_CONFIG] Discord Webhook 通知參數
    DISCORD_WEBHOOK_URL: str = ""
    DISCORD_USERNAME: str = ""
    DISCORD_TIMEOUT_SEC: int = 10
    WEBHOOK_ENABLED: bool = True

    # 環境變數 (自 .env 或 Docker Environment 自動注入)
    MOCK_HARDWARE: bool = False
    HW_MODEL: str = "UNKNOWN_MODEL"
    DEVICE_ID: str = "UNKNOWN_DEVICE"
    DOCKER_COMPOSE_FILE: str = "UNKNOWN_COMPOSE"
    OTA_SERVER_URL: str = "http://192.168.0.100:8080/"

    # version.json
    APP_VERSION: str = "v0.0.0"

    # 🛡️ 【Pydantic 強型別防呆熔斷驗證器】
    @field_validator("DISCORD_WEBHOOK_URL")
    @classmethod
    def validate_discord_url(cls, v: str) -> str:
        # 若有設定網址，才進行語法與開頭驗證
        if v and not v.startswith("https://discord.com/api/webhooks/"):
            raise ValueError("DISCORD_WEBHOOK_URL must start with 'https://discord.com/api/webhooks/'")
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


# 3. 自動化動態解析與扁平化邏輯
master_config_data = {}

for cfg_info in CONFIG_REGISTRY:
    file_path = cfg_info["path"]
    target_section = cfg_info["section"]

    # 🛡️ 【第一道安全防線】檢查設定檔是否存在
    if not os.path.exists(file_path):
        print(
            f"\n[CRITICAL ERROR] Required config file NOT found at: {file_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        parser = configparser.ConfigParser()
        parser.read(file_path, encoding="utf-8")

        if target_section not in parser:
            raise KeyError(f"Missing required '[{target_section}]' section.")

        # 自動將該 Section 下的所有 key 轉成大寫並匯入 master 字典
        for key, value in parser[target_section].items():
            master_config_data[key.upper()] = value

    except Exception as e:
        print(
            f"\n[CRITICAL ERROR] Failed to parse configurations from {file_path}",
            file=sys.stderr,
        )
        print(f"[ERROR DETAILS] {e}", file=sys.stderr)
        sys.exit(1)

# 動態讀取 version.json 並注入 APP_VERSION 至 master_config_data
version_file_path = "/workspace/version.json"
if not os.path.exists(version_file_path):
    version_file_path = os.path.join(BASE_DIR, "..", "version.json")

if os.path.exists(version_file_path):
    try:
        with open(version_file_path, "r", encoding="utf-8") as f:
            v_data = json.load(f)
            master_config_data["APP_VERSION"] = v_data.get("version", "v0.0.0")
    except Exception:
        pass

# 在交給 Pydantic 驗證前，自動將外部 MB 轉為底層需求的 Bytes
if "MAX_BYTES" in master_config_data:
    try:
        master_config_data["MAX_BYTES"] = int(master_config_data["MAX_BYTES"]) * 1024 * 1024
    except ValueError:
        pass

# 4. 🚀 【第二道安全防線】將扁平化後的字典丟給 Pydantic 進行全域型態驗證與熔斷
try:
    settings = Settings(**master_config_data)
    print(f"[SUCCESS] All hardware configurations ({len(CONFIG_REGISTRY)} files) verified and locked.")
except Exception as e:
    print(f"\n[CRITICAL ERROR] Configuration validation failed!", file=sys.stderr)
    print(f"[ERROR DETAILS] {e}", file=sys.stderr)
    print(
        "[SYSTEM HALTED] Refused to bootstrap due to parameter or type mismatch.",
        file=sys.stderr,
    )
    sys.exit(1)
