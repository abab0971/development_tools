# -*- coding: utf-8 -*-
# ==============================================================================
# File: gpio_driver.py
# Brief: GPIO 輸入輸出控制器，負責與 Raspberry Pi 的 GPIO 腳位進行互動
# Author: zhihao <zhihao8841@gmail.com>
# Created Time: 2026-05-26 23:50:00
# Copyright: Copyright (c) 2026 CQI (CHENGQI Co., Ltd.)
#            All rights reserved.
# Notice: 保留原程式碼完整性，將原本從 config 讀取的參數改為初始化參數
# ==============================================================================
import RPi.GPIO as GPIO

class GPIO_OUT_Controller:
    # 💡 最小修改：將原本的 config 變數作為參數傳入，給予預設值
    def __init__(self, pin = None, mode = GPIO.OUT, gpio_mode = "BCM", default_state = 0, cleanup = True):
        """Init GPIO Pin"""
        if pin is None:
            raise ValueError("Need to Enter the Pin Number")
        self.pin = pin
        self.mode = mode
        self.cleanup_on_exit = cleanup
        
        # 設定 GPIO 模式
        GPIO.setmode(GPIO.BCM if gpio_mode == "BCM" else GPIO.BOARD)
        
        # 根據 mode 來設定腳位
        GPIO.setup(self.pin, self.mode)
        
        # 若是輸出模式，則設置預設的輸出狀態
        if self.mode == GPIO.OUT:
            GPIO.output(self.pin, default_state)
    
    """寫入數值至輸出腳位"""
    def write(self, value):
        if self.mode == GPIO.OUT:
            GPIO.output(self.pin, value)
        else:
            raise ValueError("Cannot write to input pin.")
    
    def cleanup(self):
        """清除設定"""
        if self.cleanup_on_exit:
            GPIO.cleanup()

class GPIO_IN_Controller:
    def __init__(self, pin = None, mode = GPIO.IN, pull_up_down = None, gpio_mode = "BCM", cleanup = True):
        """Init GPIO Pin"""
        if pin is None:
            raise ValueError("Need to Enter the Pin Number")
        self.pin = pin
        self.mode = mode
        self.pull_up_down = pull_up_down
        self.cleanup_on_exit = cleanup
        
        # 設定 GPIO 模式
        GPIO.setmode(GPIO.BCM if gpio_mode == "BCM" else GPIO.BOARD)
        
        # 根據 mode 來設定腳位
        GPIO.setup(self.pin, self.mode, self.pull_up_down)
    
    """讀取輸入腳位的數值"""
    def read(self):
        if self.mode == GPIO.IN:
            return GPIO.input(self.pin)
        else:
            raise ValueError("Cannot read from output pin.")
    
    def cleanup(self):
        """清除設定"""
        if self.cleanup_on_exit:
            GPIO.cleanup()