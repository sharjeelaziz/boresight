#!/usr/bin/python2

import threading
import sys
import logging
import math
import ephem

from datetime import datetime
from time import sleep
from lsm303dlhc import LSM303DLHC
from servo import Servo

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

    def set_elements(self, new_elements):
        self.elements = new_elements
        self.log.info("Elements updated.")

    def set_location(self, latitude, longitude, altitude):
        self.home.lon = str(longitude)
        self.home.lat = str(latitude)
        self.home.elevation = altitude

    def _track_worker(self):
        """
        Runs as a thread
        """
        while self._running:
            try:
                if (len(self.elements) > 0):
                    element = self.elements[0]
                    if (len(element) == 3):
                        satellite = ephem.readtle(element[0], element[1], element[2])
                        # iss = ephem.readtle('ISS',
                        # '1 25544U 98067A   15002.52246161  .00016717  00000-0  10270-3 0  9002',
                        # '2 25544  51.6406 190.8516 0006769 204.9577 155.1248 15.52925311  2266'
                        # )

                        self.home.date = datetime.utcnow()
                        satellite.compute(self.home)
                        altitude = satellite.alt * self.degrees_per_radian
                        azimuth = satellite.az * self.degrees_per_radian
                        self.servo.set_azimuth(int(azimuth), 0)
                        self.servo.set_elevation(int(altitude), 0)
                        self.log.info('iss: altitude % 4.1f deg, azimuth % 5.1f deg' % (altitude, azimuth))
                sleep(1.0)
            except Exception as inst:
                print type(inst)    # the exception instance
                print inst.args     # arguments stored in .args
                print inst          # __str__ allows args to be printed directly
            sleep(1.0)

            # except:
            #    self.log.warn("_track_worker thread exception")
            #    sleep(1)
        self.log.debug("sending thread exit")
