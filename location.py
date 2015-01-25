#!/usr/bin/python2

import threading
import logging
import gps

from time import sleep


class Location:

    def __init__(self, location_handler, config):
        self.log = logging.getLogger('pysattracker')
        self.location_handler = location_handler
        self.config = config
        self.session = gps.gps("localhost", "2947")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self._start()
        self._running = True
        self._worker = threading.Thread(target=self._location_worker)
        self._worker.setDaemon(True)
        self._worker.start()

    def exit(self):
        self._running = False
        self._stop()

    def _start(self):
        print "Staring location module."

    def _stop(self):
        print "Stopping location module."

    def _location_worker(self):
        """
        Runs as a thread
        """
        while self._running:
            try:
                report = self.session.next()
                if report['class'] == 'TPV':
                    if hasattr(report, 'lat' and 'lon'):
                        latitude = report.lat
                        longitude = report.lon
                        altitude = report.alt
                        self.location_handler(latitude, longitude, altitude)
                        self.log.info("Updating Location")
                    if hasattr(report, 'time'):
                        gps_time = report.time

                sleep(5.0)
            except KeyError:
                    pass
            except StopIteration:
                    self.session = None
                    print "GPSD has terminated"          # __str__ allows args to be printed directly
