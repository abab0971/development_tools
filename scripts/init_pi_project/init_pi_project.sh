#!/bin/bash

# Target directory, default to current directory if not provided
TARGET_DIR="${1:-.}"

echo "📂 Preparing to create project structure in: ${TARGET_DIR}"

# Ensure target directory exists
mkdir -p "${TARGET_DIR}"

# Switch to target directory and get absolute path
cd "${TARGET_DIR}" || exit 1
ABS_PATH=$(pwd)

echo "📁 Generating Clean Architecture project layout at ${ABS_PATH}..."

# Create root-level directories
mkdir -p data mosquitto/config

# Create app directory and its subdirectories
mkdir -p app/core
mkdir -p app/infrastructure
mkdir -p app/database
mkdir -p app/api/v1
mkdir -p app/static/css
mkdir -p app/static/js
mkdir -p app/templates
mkdir -p app/tests

echo "📄 Creating base configuration files..."
touch .env .gitignore Dockerfile docker-compose.yml requirements.txt README.md
touch mosquitto/config/mosquitto.conf

echo "🐍 Creating Python modules and source files..."
touch app/__init__.py app/main.py app/config.py
touch app/core/__init__.py app/core/hardware.py app/core/interfaces.py
touch app/infrastructure/__init__.py app/infrastructure/mqtt_client.py app/infrastructure/serial_io.py app/infrastructure/i2c_bus.py
touch app/database/__init__.py app/database/connection.py app/database/crud.py
touch app/api/__init__.py app/api/v1/__init__.py app/api/v1/endpoints.py app/api/websocket.py
touch app/templates/index.html
touch app/tests/__init__.py app/tests/conftest.py app/tests/test_api.py app/tests/test_core.py

echo "✅ Project structure generated successfully!"
echo "👉 Project Path: ${ABS_PATH}"
