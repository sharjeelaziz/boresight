#!/usr/bin/python2

import threading
import sys
import logging
import math
import ephem
import time

from datetime import datetime
from lsm303dlhc import LSM303DLHC
from servo import Servo

class Satellite:
    def __init__(self):
        self.element_index = 0
        self.rise_time = None
        self.rise_azimuth = None
        self.max_alt_time = None
        self.max_alt = None
        self.set_time = None
        self.set_azimuth = None
        self.name = None

class Track:
    def __init__(self, config):
        self.degrees_per_radian = 180.0 / math.pi
        self.home = ephem.Observer()
        self.home.lon = config['home']['lng']
        self.home.lat = config['home']['lat']
        self.home.elevation = float(config['home']['alt'])

        self.elements = []
        self.satellite = Satellite()


        self.lsm = LSM303DLHC()
        self.lsm.set_declination(10, 40)
        self.servo = Servo(config, self.lsm)

        self.log = logging.getLogger('pysattracker')
        self._running = True
        self._worker = threading.Thread(target=self._track_worker)
        self._worker.setDaemon(True)
        self._worker.start()

    def exit(self):
        self._running = False
        self.servo.exit()

    def set_elements(self, new_elements):
        self.elements = new_elements
        self.log.info("Elements updated.")
        self.satellite = self.get_visible_satellite()

    def set_location(self, latitude, longitude, altitude):
        self.home.lon = str(longitude)
        self.home.lat = str(latitude)
        self.home.elevation = altitude

    def get_visible_satellite(self):
        first_sat = Satellite()
        next_sat = Satellite()
        first_element = True
        for index, element in enumerate(self.elements):
            self.home.date = datetime.utcnow()
            sat = ephem.readtle(element[0], element[1], element[2])
            sat.compute(self.home)
            next_sat.rise_time, next_sat.rise_azimuth, next_sat.max_alt_time, next_sat.max_alt, next_sat.set_time, next_sat.set_azimuth = self.home.next_pass(sat)
            next_sat.name = element[0]
            next_sat.element_index = index

            if (first_element == True):
                first_sat = next_sat
                first_element = False

            if (next_sat.rise_time.datetime() <= first_sat.rise_time.datetime()):
                first_sat = next_sat
            print ("Satellite: %s Rise time: %s azimuth: %s" % (element[0], next_sat.rise_time, next_sat.rise_azimuth))
        return first_sat

    def _track_worker(self):
        """
        Runs as a thread
        """
        sleep_interval = 2.0
        get_sat_interval = 120.0
        get_sat_next = time.time() + get_sat_interval
        while self._running:
            try:
                if (len(self.elements) > 0):
                    self.log.info('%s: Rise: %s, Azimuth: %s' % (self.satellite.name, self.satellite.rise_time, self.satellite.rise_azimuth))
                    if (datetime.utcnow() > self.satellite.rise_time.datetime() and datetime.utcnow() < self.satellite.set_time.datetime()):
                        sleep_interval = 1.0
                        element = self.elements[self.satellite.element_index]
                        if (len(element) == 3):
                            sat = ephem.readtle(element[0], element[1], element[2])
                            # iss = ephem.readtle('ISS',
                            # '1 25544U 98067A   15002.52246161  .00016717  00000-0  10270-3 0  9002',
                            # '2 25544  51.6406 190.8516 0006769 204.9577 155.1248 15.52925311  2266'
                            # )
                            self.home.date = datetime.utcnow()
                            sat.compute(self.home)
                            altitude = sat.alt * self.degrees_per_radian
                            azimuth = sat.az * self.degrees_per_radian

                            self.servo.set_azimuth(azimuth)
                            self.servo.set_elevation(altitude)
                            self.log.info('%s: altitude % 4.1f deg, azimuth % 5.1f deg' % (element[0], altitude, azimuth))
                    else:
                        sleep_interval = 5.0
                        if (time.time() > get_sat_next):
                            get_sat_next = time.time() + get_sat_interval
                            self.satellite = self.get_visible_satellite()

            except Exception as inst:
                print type(inst)    # the exception instance
                print inst.args     # arguments stored in .args
                print inst          # __str__ allows args to be printed directly
            time.sleep(sleep_interval)

            # except:
            #    self.log.warn("_track_worker thread exception")
            #    sleep(1)
        self.log.debug("sending thread exit")
