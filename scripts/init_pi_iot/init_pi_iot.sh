#!/bin/bash

TARGET_DIR="${1:-.}"
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")

echo "📂 Preparing to create Pi (IoT Core) Project in: ${TARGET_DIR}"
mkdir -p "${TARGET_DIR}"
cd "${TARGET_DIR}" || exit 1
ABS_PATH=$(pwd)

# Helper function to generate standardized python head comments
create_py_file() {
    local filepath=$1
    local desc=$2
    local filename=$(basename "$filepath")
    cat << EOF > "$filepath"
# -*- coding: utf-8 -*-
"""
File: ${filename}
Description: ${desc}
Creator: development_tools
Created Time: ${CURRENT_TIME}
"""
EOF
}

# Create Directories (Including the new app/config layer)
mkdir -p data app/common app/config/gpio app/core app/database app/infrastructure/gpio app/infrastructure/mqtt app/tests

# Create .gitkeep for empty directories to ensure Git tracking
touch data/.gitkeep

# Create Root Files
touch .env .gitignore Dockerfile docker-compose.yml requirements.txt README.md

# Create Python Files with Head Comments
create_py_file "app/__init__.py" "App package initialization."
create_py_file "app/main.py" "Application entry point for IoT core logic."
create_py_file "app/config.py" "Configuration loader using Pydantic."

create_py_file "app/common/__init__.py" "Common utilities package."
create_py_file "app/common/utils.py" "General helper functions and utility pure functions."

create_py_file "app/core/__init__.py" "Core domain logic package."
create_py_file "app/core/hardware.py" "Core hardware state machine and business use cases."
create_py_file "app/core/interfaces.py" "Abstract interfaces for hardware and notifying services."

create_py_file "app/database/__init__.py" "Database layer initialization."
create_py_file "app/database/connection.py" "SQLite database connection and session management."
create_py_file "app/database/crud.py" "Database CRUD operations."

create_py_file "app/infrastructure/__init__.py" "Infrastructure layer initialization."
create_py_file "app/infrastructure/gpio/__init__.py" "GPIO standalone driver package."
create_py_file "app/infrastructure/gpio/gpio_drivers.py" "Independent GPIO IN/OUT controller implementation."
create_py_file "app/infrastructure/mqtt/__init__.py" "MQTT standalone client package."
create_py_file "app/infrastructure/mqtt/mqtt_client.py" "Independent MQTT Client integration."

create_py_file "app/tests/__init__.py" "Test suite initialization."
create_py_file "app/tests/conftest.py" "Pytest global configuration and hardware mocks."
create_py_file "app/tests/test_core.py" "Unit tests for core hardware and business logic."

# Create Configuration File (INI format) with standardized head comments
cat << EOF > "app/config/gpio/gpio.cfg"
# -*- coding: utf-8 -*-
# File: gpio.cfg
# Description: Specific feature configuration for GPIO module.
# Creator: development_tools
# Created Time: ${CURRENT_TIME}

[pins]
green_led_pin = 17
red_led_pin = 27
yellow_led_pin = 22
lock_out_pin = 5
lock_in_pin = 6
EOF

echo "✅ Pi (IoT Core) Project structure generated successfully!"
echo "👉 Project Path: ${ABS_PATH}"