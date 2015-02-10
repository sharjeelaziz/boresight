#!/usr/bin/python2

import threading
import sys
import logging
import math
import ephem
import time
import copy

from datetime import datetime
from lsm303dlhc import LSM303DLHC
from servo import Servo

class Satellite:
    def __init__(self, element_index=0, rise_time=None, rise_azimuth=None, max_alt_time=None, max_alt=None, set_time=None, set_azimuth=None, name=None):
        self.element_index = element_index
        self.rise_time = rise_time
        self.rise_azimuth = rise_azimuth
        self.max_alt_time = max_alt_time
        self.max_alt = max_alt
        self.set_time = set_time
        self.set_azimuth = set_azimuth
        self.name = name

class Track:
    def __init__(self, config):
        self.degrees_per_radian = 180.0 / math.pi
        self.home = ephem.Observer()
        self.home.lon = config['home']['lng']
        self.home.lat = config['home']['lat']
        self.home.elevation = float(config['home']['alt'])

        self.elements = []

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


    def set_location(self, latitude, longitude, altitude):
        self.home.lon = str(longitude)
        self.home.lat = str(latitude)
        self.home.elevation = altitude

    def get_visible_satellite(self):
        first_sat = Satellite()
        first_element = True
        for index, element in enumerate(self.elements):
            self.home.date = datetime.utcnow()
            sat = ephem.readtle(element[0], element[1], element[2])
            sat.compute(self.home)
            rise_time, rise_azimuth, max_alt_time, max_alt, set_time, set_azimuth = self.home.next_pass(sat)
            name = element[0]
            element_index = index

            if (first_element == True or rise_time.datetime() <= first_sat.rise_time.datetime()):
                first_element = False
                first_sat = Satellite(element_index, rise_time, rise_azimuth, max_alt_time, max_alt, set_time, set_azimuth, name)
                print ("Found Satellite: %s Rise time: %s azimuth: %s" % (first_sat.name, first_sat.rise_time, first_sat.rise_azimuth))

            print ("Satellite: %s Rise time: %s azimuth: %s" % (name, rise_time, rise_azimuth))
        return first_sat

    def _track_worker(self):
        """
        Runs as a thread
        """
        sleep_interval = 2.0
        get_sat_interval = 120.0
        get_sat_next = time.time()
        satellite = Satellite()

        while self._running:
            try:
                if (len(self.elements) > 0):
                    self.log.info('%s: Rise: %s, Azimuth: %s' % (satellite.name, satellite.rise_time, satellite.rise_azimuth))
                    if (satellite.rise_time is not None and datetime.utcnow() > satellite.rise_time.datetime() and datetime.utcnow() < satellite.set_time.datetime()):
                        sleep_interval = 1.0
                        element = self.elements[satellite.element_index]
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
                            satellite = self.get_visible_satellite()

            except Exception as inst:
                print type(inst)    # the exception instance
                print inst.args     # arguments stored in .args
                print inst          # __str__ allows args to be printed directly
            time.sleep(sleep_interval)

            # except:
            #    self.log.warn("_track_worker thread exception")
            #    sleep(1)
        self.log.debug("sending thread exit")
