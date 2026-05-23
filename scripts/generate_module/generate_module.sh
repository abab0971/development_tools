#!/bin/bash

BASE_PATH="${1:-.}"
MODULE_NAME="$2"
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")

TARGET_MODULE_DIR="${BASE_PATH}/${MODULE_NAME}"

echo "📦 Preparing to generate custom module block at: ${TARGET_MODULE_DIR}"
mkdir -p "${TARGET_MODULE_DIR}"

# Helper to generate custom module python files with empty Brief and Author
create_empty_module_file() {
    local filepath=$1
    local filename=$(basename "$filepath")
    cat << EOF > "$filepath"
# -*- coding: utf-8 -*-
"""
File: ${filename}
Brief: 
Author: 
Created Time: ${CURRENT_TIME}
Copyright: Copyright (c) 2026 公司名 (MyCompany Co., Ltd.)
           All rights reserved.
Notice: 
"""
EOF
}

# Generate package files
create_empty_module_file "${TARGET_MODULE_DIR}/__init__.py"
create_empty_module_file "${TARGET_MODULE_DIR}/main.py"

cd "${TARGET_MODULE_DIR}" || exit 1
ABS_MODULE_PATH=$(pwd)

echo "✅ Custom module block [${MODULE_NAME}] generated with empty Brief & Author fields!"
echo "👉 Location: ${ABS_MODULE_PATH}"