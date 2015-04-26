#!/usr/bin/python2

import RPi.GPIO as GPIO
import logging


class Power:
    def __init__(self, config):
        self.relay_one = 17
        self.relay_two = 27
        self.relay_three = 22
        self.relay_four = 5

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        pinList = [self.relay_one, self.relay_two, self.relay_three, self.relay_four]

        for relay in pinList:
            GPIO.setup(relay, GPIO.OUT)
            GPIO.output(relay, GPIO.HIGH)

    def set_relay_one_on(self):
        GPIO.output(self.relay_one, GPIO.LOW)
        return

    def set_relay_one_off(self):
        GPIO.output(self.relay_one, GPIO.HIGH)
        return

    def set_relay_two_on(self):
        GPIO.output(self.relay_two, GPIO.LOW)
        return

    def set_relay_two_off(self):
        GPIO.output(self.relay_two, GPIO.HIGH)
        return

    def set_relay_three_on(self):
        GPIO.output(self.relay_three, GPIO.LOW)
        return

    def set_relay_three_off(self):
        GPIO.output(self.relay_three, GPIO.HIGH)
        return

    def set_relay_four_on(self):
        GPIO.output(self.relay_four, GPIO.LOW)
        return

    def set_relay_four_off(self):
        GPIO.output(self.relay_four, GPIO.HIGH)
        return

    def cleanup(self):
        GPIO.cleanup()

if __name__ == '__main__':

    config = {}

    pwr = Power(config)
    pwr.set_relay_one_on()
    pwr.set_relay_one_off()
    pwr.set_relay_two_on()
    pwr.set_relay_two_off()
    pwr.set_relay_three_on()
    pwr.set_relay_three_off()
    pwr.set_relay_four_on()
    pwr.set_relay_four_off()
    pwr.cleanup()
