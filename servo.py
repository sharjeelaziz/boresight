#!/usr/bin/python2

import threading
import sys
import logging

from pca9685 import PCA9685
from datetime import datetime
from time import sleep

class Servo:
    def __init__(self, config, lsm):

        self.pwm = PCA9685(0x40)
        self.pwm.set_pwm_freq(60)

        self.lsm = lsm

        self.pan_channel = 0
        self.tilt_channel = 1

        self.target_degrees = 90
        self.elevation = 90

        self.pan_servo_max = 562
        self.pan_servo_min = 255
        self.pan_servo_deg = self.lsm.get_heading()

        self.tilt_servo_max = 410 # 0 degrees
        self.tilt_servo_min = 338 # 90 degrees

        self.log = logging.getLogger('pysattracker')
        self._running = True
        self._worker = threading.Thread(target=self._servo_worker)
        self._worker.setDaemon(True)
        self._worker.start()

    def exit(self):
        self._running = False

    def set_azimuth(self, degrees):
        if (degrees >= 0 and degrees <= 359):
            self.target_degrees = degrees
        else:
            self.target_degrees = 0
            self.log.error("Invalid azimuth value specified.")
        self.log.info("Azimuth updated.")

    def set_elevation(self, degrees):
        if (degrees >= 0 and degrees <= 90):
            self.elevation = degrees
        else:
            self.elevation = 0
            self.log.error("Invalid elevation value received.")
        self.log.info("Elevation updated.")

    def calibrate(self):
        self.move_pan_servo(self.pan_servo_min)
        self.pan_servo_deg = self.lsm.get_heading()

    def get_pan_direction(self):
        current_degrees = self.lsm.get_heading()
        heading_delta = abs(current_degrees - self.target_degrees)

        servo_delta = abs(int(heading_delta * (float(self.pan_servo_max - self.pan_servo_min) / 360)))

        servo_cur = self.get_pan_servo_cur()

        if (current_degrees > self.target_degrees):
            pulse = servo_cur + servo_delta
        else:
            pulse = servo_cur - servo_delta

        if (pulse < self.pan_servo_min):
            pulse = self.pan_servo_min - pulse
            pulse = self.pan_servo_max - pulse
        elif (pulse > self.pan_servo_max):
            pulse = pulse - self.pan_servo_max
            pulse = self.pan_servo_min + pulse
        else:
            if (current_degrees > self.target_degrees):
                pulse = servo_cur + (servo_delta/2)
            else:
                pulse = servo_cur - (servo_delta/2)

        return pulse

    def get_tilt(self):
        tilt = self.tilt_servo_max - abs(int(self.elevation * (float(self.tilt_servo_max - self.tilt_servo_min) / 90)))

        return tilt

    def get_pan_servo_cur(self):
        servo_cur = self.pwm.get_pwm(self.pan_channel)
        if (servo_cur < self.pan_servo_min):
            servo_cur = self.pan_servo_min
        if (servo_cur > self.pan_servo_max):
            servo_cur = self.pan_servo_max
        return servo_cur

    def get_tilt_servo_cur(self):
        servo_cur = self.pwm.get_pwm(self.tilt_channel)
        if (servo_cur < self.tilt_servo_min):
            servo_cur = self.tilt_servo_min
        if (servo_cur > self.tilt_servo_max):
            servo_cur = self.tilt_servo_max
        return servo_cur

    def move_pan_servo(self, pulse_length):
        servo_cur = self.get_pan_servo_cur()
        if (pulse_length >= self.pan_servo_min and pulse_length <= self.pan_servo_max):
            if (pulse_length > servo_cur):
                for x in range(servo_cur, pulse_length, 1):
                    sleep(.1)
                    self.pwm.set_pwm(self.pan_channel, 0, x)
            else:
                for x in range(servo_cur, pulse_length, -1):
                    sleep(.1)
                    self.pwm.set_pwm(self.pan_channel, 0, x)
        return

    def move_tilt_servo(self, pulse_length):
        servo_cur = self.get_tilt_servo_cur()
        if (pulse_length >= self.tilt_servo_min and pulse_length <= self.tilt_servo_max):
            if (pulse_length > servo_cur):
                for x in range(servo_cur, pulse_length, 1):
                    sleep(.1)
                    self.pwm.set_pwm(self.tilt_channel, 0, x)
            else:
                for x in range(servo_cur, pulse_length, -1):
                    sleep(.1)
                    self.pwm.set_pwm(self.tilt_channel, 0, x)
        return

    def _servo_worker(self):
        """
        Runs as a thread
        """
        sleep(3.0)
        self.calibrate()

        while self._running:
            try:

                direction = self.get_pan_direction()
                self.move_pan_servo(direction)

                tilt = self.get_tilt()
                self.move_tilt_servo(tilt)

                self.log.info("Direction: %d Current: %d Heading: %d Target Heading: %d Tilt: %d" % (direction,
                    self.pwm.get_pwm(self.pan_channel), self.lsm.get_heading(), self.target_degrees, tilt))

                sleep(0.5)

            except Exception as inst:
                self.log.warn("_servo_worker thread exception")
                print type(inst)    # the exception instance
                print inst.args     # arguments stored in .args
                print inst          # __str__ allows args to be printed directly

        self.log.debug("sending thread exit")

if __name__ == '__main__':

    from time import sleep
    from lsm303dlhc import LSM303DLHC

    config = {}

    lsm = LSM303DLHC()
    lsm.set_declination(10, 40)

    servo = Servo(config, lsm)
    servo.set_azimuth(340)
    servo.set_elevation(0)

    while True:
        sleep(1) # Output is fun to watch if this is commented out
