# -*- coding: utf-8 -*-
# ==============================================================================
# File: utils.py
# Brief: 全域純函數、通用輔助與運算工具模組
# Author: Jim Hsu (aba0971@gmail.com)
# Created Time: 2026-09-14 00:00:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice:
# ==============================================================================
import re


def split_counting_to_digits(counting: int) -> list:
    """
    將整數計數轉換為 4 位數的陣列。
    例如：傳入 12 ➡️ 回傳 [0, 0, 1, 2]
    """
    counting = max(0, min(9999, counting))
    return [
        int((counting / 1000) % 10),
        int((counting / 100) % 10),
        int((counting / 10) % 10),
        int(counting % 10),
    ]


def parse_version_to_digits(version_str: str) -> list:
    """
    解析版本號字串並轉換為 4 位數字陣列。
    範例：
      'v0.3.0'   -> [0, 0, 3, 0]
      'v3.0.14'  -> [3, 0, 1, 4]
      'v12.3.45' -> [2, 3, 4, 5] (超過4位保留後4位)
    """
    raw_numbers = re.findall(r"\d+", str(version_str))
    all_digits = []
    for num in raw_numbers:
        for char in num:
            all_digits.append(int(char))

    if not all_digits:
        return [0, 0, 0, 0]

    if len(all_digits) > 4:
        return all_digits[-4:]
    else:
        return [0] * (4 - len(all_digits)) + all_digits
