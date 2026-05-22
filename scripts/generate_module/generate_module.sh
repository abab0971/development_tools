#!/bin/bash

BASE_PATH="${1:-.}"
MODULE_NAME="$2"
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")

# Combine paths to create target module folder
TARGET_MODULE_DIR="${BASE_PATH}/${MODULE_NAME}"

echo "📦 Preparing to generate custom module block at: ${TARGET_MODULE_DIR}"
mkdir -p "${TARGET_MODULE_DIR}"

# Helper to create customized file with empty description
create_custom_file() {
    local filepath=$1
    local filename=$(basename "$filepath")
    cat << EOF > "$filepath"
# -*- coding: utf-8 -*-
"""
File: ${filename}
Description: 
Creator: development_tools
Created Time: ${CURRENT_TIME}
"""
EOF
}

# Generate files
create_custom_file "${TARGET_MODULE_DIR}/__init__.py"
create_custom_file "${TARGET_MODULE_DIR}/main.py"

# Resolve absolute path for display
cd "${TARGET_MODULE_DIR}" || exit 1
ABS_MODULE_PATH=$(pwd)

echo "✅ Custom module block [${MODULE_NAME}] successfully generated!"
echo "👉 Location: ${ABS_MODULE_PATH}"