# ==============================================================================
# File: Dockerfile
# Brief: 跨平台多階段 Docker 映像檔編譯藍圖 (Pi 5 & Pi Zero 2W 雙平台極致輕量版)
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-05-30
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 
# ==============================================================================

# 官方極輕量 Python 3.11 Slim (Bookworm)
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Taipei

# 安裝 gcc, sqlite3, libgpiod-dev 與 tzdata 時區庫
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    sqlite3 \
    libsqlite3-dev \
    libgpiod-dev \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# 複製並安裝 Python 套件 (使用 --no-cache-dir 避免快取佔用寶貴的 SD 卡空間)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

# 啟動背景 IoT 核心管理程序
CMD ["python", "-m", "app.main"]