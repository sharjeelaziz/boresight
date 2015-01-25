#!/usr/bin/python2

import threading
import sys
import logging

from Adafruit_PWM_Servo_Driver import PWM
from datetime import datetime
from time import sleep


class Servo:
    def __init__(self, config, lsm):

        self.pwm = PWM(0x40)
        self.pwm.setPWMFreq(60)

        self.lsm = lsm

        self.pan_channel = 0
        self.tilt_channel = 1

        self.target_degrees = 0
        self.target_minutes = 0
        self.elevation = 0

        self.pan_servo_max = 580
        self.pan_servo_min = 250
        self.pan_servo_cur = 250

        self.tilt_servo_max = 420 # 0 degrees (520) is max
        #self.tilt_servo_min = 280 # 87 degrees
        self.tilt_servo_min = 270 # 87 degrees

        self.log = logging.getLogger('pysattracker')
        self._running = True
        self._worker = threading.Thread(target=self._servo_worker)
        self._worker.setDaemon(True)
        self._worker.start()

    def exit(self):
        self._running = False

    def set_azimuth(self, degrees, minutes):
        if (degrees >= 0 and degrees <= 359):
            self.target_degrees = degrees
            self.target_minutes = minutes
        else:
            self.target_degrees = 0
            self.target_minutes = 0
            self.log.error("Invalid azimuth value specified.")
        self.log.info("Azimuth updated.")

    def set_elevation(self, degrees, minutes):
        if (degrees >= 3 and degrees <= 90):
            self.elevation = degrees
        else:
            self.elevation = 3

        self.log.error("Invalid elevation value received.")
        self.log.info("Elevation updated.")

    def get_pan_direction(self):
        direction = 0
        (current_degrees, current_minutes) = self.lsm.get_heading()

        heading_delta = self.target_degrees - current_degrees

        servo_delta = abs(int(heading_delta * (float(self.pan_servo_max - self.pan_servo_min) / 180)))

        print heading_delta
        print servo_delta

        increment_value = 1
        if (servo_delta > 5):
            increment_value = servo_delta - 5

        print increment_value

        if (self.target_degrees > current_degrees):
            direction = increment_value;
        elif (self.target_degrees < current_degrees):
            direction = -increment_value;
        return direction

    def get_tilt(self):
        tilt = self.tilt_servo_max - abs(int(self.elevation * (float(self.tilt_servo_max - self.tilt_servo_min) / 90)))
        print tilt

        return tilt

    def move_pan_servo(self, pulse_length):
        new_pulse_length = self.pan_servo_cur + pulse_length
        if (new_pulse_length >= self.pan_servo_min and new_pulse_length <= self.pan_servo_max):
            self.pwm.setPWM(self.pan_channel, 0, new_pulse_length)
            self.pan_servo_cur = new_pulse_length
        return

    def move_tilt_servo(self, pulse_length):
        if (pulse_length >= self.tilt_servo_min and pulse_length <= self.tilt_servo_max):
            self.pwm.setPWM(self.tilt_channel, 0, pulse_length)
        return

    def _servo_worker(self):
        """
        Runs as a thread
        """
        while self._running:
            try:
                direction = self.get_pan_direction()
                self.move_pan_servo(direction)
                print direction
                print self.pan_servo_cur
                print self.lsm.get_heading()

                tilt = self.get_tilt()
                self.move_tilt_servo(tilt)

                sleep(2.0)

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
    servo.set_azimuth(150, 0)
    servo.set_elevation(45, 0)

    while True:
        sleep(1) # Output is fun to watch if this is commented out
