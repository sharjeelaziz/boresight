#!/usr/bin/python2

import time
import math
from Adafruit_I2C import Adafruit_I2C

class PCA9685:
    MODE1              = 0x00
    MODE2              = 0x01
    SUBADR1            = 0x02
    SUBADR2            = 0x03
    SUBADR3            = 0x04
    PRESCALE           = 0xFE
    LED0_ON_L          = 0x06
    LED0_ON_H          = 0x07
    LED0_OFF_L         = 0x08
    LED0_OFF_H         = 0x09
    ALL_LED_ON_L       = 0xFA
    ALL_LED_ON_H       = 0xFB
    ALL_LED_OFF_L      = 0xFC
    ALL_LED_OFF_H      = 0xFD

    RESTART            = 0x80
    SLEEP              = 0x10
    ALLCALL            = 0x01
    INVRT              = 0x10
    OUTDRV             = 0x04

    def __init__(self, address=0x40):
        self.i2c = Adafruit_I2C(address)
        self.address = address

        #self.set_all_pwm(0, 0)
        self.i2c.write8(self.MODE2, self.OUTDRV)
        self.i2c.write8(self.MODE1, self.ALLCALL)
        time.sleep(0.005)                                       # wait for oscillator

        mode1 = self.i2c.readU8(self.MODE1)
        mode1 = mode1 & ~self.SLEEP                 # wake up (reset sleep)
        self.i2c.write8(self.MODE1, mode1)
        time.sleep(0.005)                             # wait for oscillator

    def set_pwm_freq(self, freq):
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)

        oldmode = self.i2c.readU8(self.MODE1);
        newmode = (oldmode & 0x7F) | 0x10             # sleep
        self.i2c.write8(self.MODE1, newmode)        # go to sleep
        self.i2c.write8(self.PRESCALE, int(math.floor(prescale)))
        self.i2c.write8(self.MODE1, oldmode)
        time.sleep(0.005)
        self.i2c.write8(self.MODE1, oldmode | 0x80)

    def set_pwm(self, channel, on, off):
        self.i2c.write8(self.LED0_ON_L+4*channel, on & 0xFF)
        self.i2c.write8(self.LED0_ON_H+4*channel, on >> 8)
        self.i2c.write8(self.LED0_OFF_L+4*channel, off & 0xFF)
        self.i2c.write8(self.LED0_OFF_H+4*channel, off >> 8)

    def set_all_pwm(self, on, off):
        self.i2c.write8(self.ALL_LED_ON_L, on & 0xFF)
        self.i2c.write8(self.ALL_LED_ON_H, on >> 8)
        self.i2c.write8(self.ALL_LED_OFF_L, off & 0xFF)
        self.i2c.write8(self.ALL_LED_OFF_H, off >> 8)

    def get_pwm(self, channel):
        pos = (self.i2c.readU8(self.LED0_OFF_L+channel*4) + ((self.i2c.readU8(self.LED0_OFF_H+channel*4)<<8)))
        return pos
