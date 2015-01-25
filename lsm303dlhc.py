#!/usr/bin/python

import math

from Adafruit_I2C import Adafruit_I2C


class LSM303DLHC:

    # Linear Acceleration Registers
                            # Type  Hex  Binary  Default
    CTRL_REG1_A = 0x20      # rw    0x20 010 0000 00000111 Data rate config
    CTRL_REG2_A = 0x21      # rw    0x21 010 0001 00000000
    CTRL_REG3_A = 0x22      # rw    0x22 010 0010 00000000
    CTRL_REG4_A = 0x23      # rw    0x23 010 0011 00000000
    CTRL_REG5_A = 0x24      # rw    0x24 010 0100 00000000
    CTRL_REG6_A = 0x25      # rw    0x25 010 0101 00000000
    REFERENCE_A = 0x26      # rw    0x26 010 0110 00000000
    STATUS_REG_A = 0x27     # r     0x27 010 0111 00000000
    OUT_X_L_A = 0x28        # r     0x28 010 1000 output
    OUT_X_H_A = 0x29        # r     0x29 010 1001 output
    OUT_Y_L_A = 0x2A        # r     0x2A 010 1010 output
    OUT_Y_H_A = 0x2B        # r     0x2B 010 1011 output
    OUT_Z_L_A = 0x2C        # r     0x2C 010 1100 output
    OUT_Z_H_A = 0x2D        # r     0x2D 010 1101 output
    FIFO_CTRL_REG_A = 0x2E  # rw    0x2E 010 1110 00000000
    FIFO_SRC_REG_A = 0x2F   # r     0x2F 010 1111
    INT1_CFG_A = 0x30       # rw    0x30 011 0000 00000000
    INT1_SRC_A = 0x31       # r     0x31 011 0001 00000000
    INT1_THS_A = 0x32       # rw    0x32 011 0010 00000000
    INT1_DURATION_A = 0x33  # rw    0x33 011 0011 00000000
    INT2_CFG_A = 0x34       # rw    0x34 011 0100 00000000
    INT2_SRC_A = 0x35       # r     0x35 011 0101 00000000
    INT2_THS_A = 0x36       # rw    0x36 011 0110 00000000
    INT2_DURATION_A = 0x37  # rw    0x37 011 0111 00000000
    CLICK_CFG_A = 0x38      # rw    0x38 011 1000 00000000
    CLICK_SRC_A = 0x39      # rw    0x39 011 1001 00000000
    CLICK_THS_A = 0x3A      # rw    0x3A 011 1010 00000000
    TIME_LIMIT_A = 0x3B     # rw    0x3B 011 1011 00000000
    TIME_LATENCY_A = 0x3C   # rw    0x3C 011 1100 00000000
    TIME_WINDOW_A =  0x3D   # rw    0x3D 011 1101 00000000

    # Magnetic sensor registers
    CRA_REG_M = 0x00        # rw    0x00 00000000 0001000
    CRB_REG_M = 0x01        # rw    0x01 00000001 0010000
    MR_REG_M = 0x02         # rw    0x02 00000010 00000011 Magnetic sensor operating mode
    OUT_X_H_M = 0x03        # r     0x03 00000011 output
    OUT_X_L_M = 0x04        # r     0x04 00000100 output
    OUT_Z_H_M = 0x05        # r     0x05 00000101 output
    OUT_Z_L_M = 0x06        # r     0x06 00000110 output
    OUT_Y_H_M = 0x07        # r     0x07 00000111 output
    OUT_Y_L_M = 0x08        # r     0x08 00001000 output
    SR_REG_M = 0x09         # r     0x09 00001001 00000000
    IRA_REG_M = 0x0A        # r     0x0A 00001010 01001000
    IRB_REG_M = 0x0B        # r     0x0B 00001011 00110100
    IRC_REG_M = 0x0C        # r     0x0C 00001100 00110011

    # Temperature registers
    TEMP_OUT_H_M = 0x31     # 0x31 00000000 output
    TEMP_OUT_L_M = 0x32     # 0x32 00000000 output

    MAG_GAIN_1_3 = 0b00100000 # +-1.3 1100 980
    MAG_GAIN_1_9 = 0b01000000 # +-1.9 855 760
    MAG_GAIN_2_5 = 0b01100000 # +-2.5 670 600
    MAG_GAIN_4_0 = 0b10000000 # +-4.0 450 400
    MAG_GAIN_4_7 = 0b10100000 # +-4.7 400 355
    MAG_GAIN_5_6 = 0b11000000 # +-5.6 330 295
    MAG_GAIN_8_1 = 0b11100000 # +-8.1 230 205

    # For linear acceleration the default (factory) 7-bit slave address is 0011001b.
    # For magnetic sensors the default (factory) 7-bit slave address is 0011110xb.

    LINEAR_ACCELERATOR_ADDRESS = (0x32 >> 1)
    MAGNETIC_SENSOR_ADDRESS = (0x3C >> 1)

    def __init__(self, bus_num=-1):
        self.declination = 0

        self.accelerometer = Adafruit_I2C(self.LINEAR_ACCELERATOR_ADDRESS, bus_num)

        # enable all axis and set data rate to 100Hz
        self.accelerometer.write8(self.CTRL_REG1_A, 0b01010111);

        # FS1FS0HR00 +-8g, high resolution
        self.accelerometer.write8(self.CTRL_REG4_A, 0b00101000);

        self.magnetometer = Adafruit_I2C(self.MAGNETIC_SENSOR_ADDRESS, bus_num)

        # place magnetometer in continuous conversion mode
        self.magnetometer.write8(self.MR_REG_M, 0x00)

    def set_magnetometer_gain(self, gain=MAG_GAIN_1_3):
        self.magnetometer.write8(CRB_REG_M, gain)

    def set_declination(self, degree, minutes = 0):
        self.declination = (degree + minutes/60) * (math.pi/180)

    def accel12(self, list, idx):
        n = list[idx] | (list[idx+1] << 8) # Low, high bytes

        # 2's complement signed
        if n > 32767:
            n -= 65536
        return n >> 4 # 12-bit resolution

    def mag16(self, list, idx):
        n = (list[idx] << 8) | list[idx+1]   # High, low bytes
        return n if n < 32768 else n - 65536 # 2's complement signed

    def read_accelerometer(self):
        list = self.accelerometer.readList(self.OUT_X_L_A | 0x80, 6)
        res = [( self.accel12(list, 0),
                 self.accel12(list, 2),
                 self.accel12(list, 4) )]

        return res

    def read_magnetometer(self):
        list = self.magnetometer.readList(self.OUT_X_H_M, 6)
        res  = [(self.mag16(list, 0),
                    self.mag16(list, 2),
                    self.mag16(list, 4))]

        return res

    def get_heading(self):

        list = self.magnetometer.readList(self.OUT_X_H_M, 6)
        mag_x = self.mag16(list, 0)
        mag_z = self.mag16(list, 2)
        mag_y = self.mag16(list, 4)

        heading_rad = math.atan2(mag_y, mag_x)
        heading_rad += self.declination

        if (heading_rad < 0):
            heading_rad += 2*math.pi

        if (heading_rad > 2*math.pi):
            heading_rad -= 2*math.pi

        heading_deg = heading_rad*180/math.pi

        degrees = math.floor(heading_deg)
        minutes = round(((heading_deg - degrees) * 60))

        return (int(degrees), int(minutes))

if __name__ == '__main__':

    from time import sleep

    lsm = LSM303DLHC()
    lsm.set_declination(10, 40)

    while True:
        (degrees, minutes) = lsm.get_heading()
        print degrees
        print minutes
        sleep(1) # Output is fun to watch if this is commented out

