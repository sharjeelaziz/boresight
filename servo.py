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

        self.target_degrees = 90
        self.elevation = 90

        self.pan_servo_max = 600
        self.pan_servo_min = 300
        self.pan_servo_cur = 300
        self.pan_servo_deg = self.lsm.get_heading()

        self.tilt_servo_max = 530 # 0 degrees
        self.tilt_servo_min = 270 # 90 degrees

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
        if (degrees >= 3 and degrees <= 90):
            self.elevation = degrees
        else:
            self.elevation = 3
            self.log.error("Invalid elevation value received.")
        self.log.info("Elevation updated.")

    def calibrate(self):
        self.pwm.setPWM(self.pan_channel, 0, self.pan_servo_min)
        self.pan_servo_cur = self.pan_servo_min
        sleep(3.0)
        self.pan_servo_deg = self.lsm.get_heading()

    def get_pan_direction(self):
        current_degrees = self.lsm.get_heading()
        heading_delta = abs(current_degrees - self.target_degrees)

        servo_delta = abs(int(heading_delta * (float(self.pan_servo_max - self.pan_servo_min) / 360))) / 2

        if (current_degrees > self.target_degrees):
            pulse = self.pan_servo_cur + servo_delta
        else:
            pulse = self.pan_servo_cur - servo_delta

        if (pulse < self.pan_servo_min):
            pulse = self.pan_servo_min - pulse
            pulse = self.pan_servo_max - pulse
        elif (pulse > self.pan_servo_max):
            pulse = pulse - self.pan_servo_max
            pulse = self.pan_servo_min + pulse

        print "Current heading %d" % (self.lsm.get_heading())
        print "Target heading %d" % (self.target_degrees)
        print "Pulse %d" % (pulse)

        return pulse

    def get_pan_goto(self):

        current_degrees = self.lsm.get_heading()
        heading_delta = abs(current_degrees - self.target_degrees)

        zero_degree_pulse = abs(int(self.pan_servo_deg * (float(self.pan_servo_max - self.pan_servo_min) / 360))) + self.pan_servo_min

        if (self.target_degrees > self.pan_servo_deg):
            pulse = zero_degree_pulse + abs(int((360 - self.target_degrees) * (float(self.pan_servo_max - self.pan_servo_min) / 360)))
        else:
            pulse = zero_degree_pulse - abs(int((self.target_degrees) * (float(self.pan_servo_max - self.pan_servo_min) / 360)))

        print "Current heading %d" % (self.lsm.get_heading())
        print "Pan min degrees %d" % (self.pan_servo_deg)
        print "Target heading %d" % (self.target_degrees)
        print "Pulse %d" % (pulse)

        return pulse

    def get_tilt(self):
        tilt = self.tilt_servo_max - abs(int(self.elevation * (float(self.tilt_servo_max - self.tilt_servo_min) / 90)))
        print "Tile %d" % (tilt)

        return tilt

    def move_pan_servo(self, pulse_length):
        if (pulse_length >= self.pan_servo_min and pulse_length <= self.pan_servo_max):
            print "Moving to %d" % (pulse_length)
            self.pwm.setPWM(self.pan_channel, 0, pulse_length)
            self.pan_servo_cur = pulse_length
        return

    def move_tilt_servo(self, pulse_length):
        if (pulse_length >= self.tilt_servo_min and pulse_length <= self.tilt_servo_max):
            self.pwm.setPWM(self.tilt_channel, 0, pulse_length)
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

                print "Direction %d" % (direction)
                print "Current servo %d" % (self.pan_servo_cur)
                print "Current heading %d" % (self.lsm.get_heading())
                print "****"

                tilt = self.get_tilt()
                self.move_tilt_servo(tilt)

                sleep(1.0)

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
    servo.set_azimuth(300)
    servo.set_elevation(45)

    while True:
        sleep(1) # Output is fun to watch if this is commented out
