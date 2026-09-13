# -*- coding: utf-8 -*-
# ==============================================================================
# File: discord_client.py
# Brief: Discord Webhook 客戶端實作，使用原生 Python urllib 套件進行 HTTP POST 請求
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice:
# ==============================================================================
import json
import urllib.request
import urllib.error
from app.core.interfaces import IWebhookAgent, ILogger


class DiscordWebhookClient(IWebhookAgent):
    """
    Discord Webhook 客戶端實作，使用原生 Python urllib 套件進行 HTTP POST 請求。
    """

    def __init__(self, webhook_url: str, username: str, timeout_sec: int, logger: ILogger):
        self.webhook_url = webhook_url
        self.username = username
        self.timeout_sec = timeout_sec
        self.logger = logger

    def send_message(self, message: str) -> bool:
        if not self.webhook_url:
            self.logger.warning("[WEBHOOK WARN] DISCORD_WEBHOOK_URL is empty. Suppressing dispatch.")
            return False

        payload = {"username": self.username or "IoT_Device_Notify", "content": message}
        try:
            self.logger.info("[WEBHOOK HTTP] Dispatching Discord webhook payload...")
            json_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.webhook_url,
                data=json_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Test/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as response:
                status_code = response.getcode()
                if status_code in (200, 204):
                    self.logger.info(f"[WEBHOOK HTTP SUCCESS] Delivered successfully (HTTP {status_code}).")
                    return True
                else:
                    self.logger.error(f"[WEBHOOK HTTP REFUSED] Server responded with status: {status_code}")
                    return False
        except urllib.error.HTTPError as e:
            self.logger.error(f"[WEBHOOK HTTP ERROR] HTTP status code: {e.code}, Reason: {e.reason}")
            return False
        except urllib.error.URLError as e:
            self.logger.error(f"[WEBHOOK HTTP ERROR] Network connection failed. Reason: {e.reason}")
            return False
        except Exception as e:
            self.logger.error(f"[WEBHOOK HTTP ERROR] Unexpected exception: {str(e)}")
            return False
