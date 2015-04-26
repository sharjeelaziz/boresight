#!/usr/bin/python2

import urllib2
import threading
import logging

from time import sleep


class NetTle:

    def __init__(self, tle_handler, config):
        self.log = logging.getLogger('boresight')
        self.tle_handler = tle_handler
        self.config = config
        self.satellites = self.config['sats']
        self.url = self.config['tle_url']
        self._start()
        self._running = True
        self._worker = threading.Thread(target=self._tle_worker)
        self._worker.setDaemon(True)
        self._worker.start()

    def group_tles(self, lst, n):
        for i in xrange(0, len(lst), n):
            yield lst[i:i+n]

    def read_tle(self, url):
        response = urllib2.urlopen(url)
        data = response.read()
        data = data.replace("\r\n", "\n")
        data = data.split('\n')
        s = self.group_tles(data, 3)
        return s

    def get_tle(self, url, name):
        data = self.read_tle(url)
        element = filter(lambda x: x[0].find(name) != -1, data)
        return element

    def get_all_tle(self, url):
        tles = []
        s = self.read_tle(url)
        for element in s:
            tles.append(element)
        return tles

    def get_selected_tle(self, satellites, url):
        elements = []
        s = self.read_tle(url)
        for element in s:
            if (element[0] in satellites):
                elements.append(element)
        return elements

    def exit(self):
        self._running = False
        self._stop()

    def _start(self):
        self.log.info("Staring TLE Module.")

    def _stop(self):
        self.log.info("Stopping TLE Module.")

    def _tle_worker(self):
        """
        Runs as a thread
        """
        while self._running:
            try:
                elements = self.get_selected_tle(self.satellites, self.url)
                self.log.info("Downloading elements.")
                if (len(elements) > 0):
                    self.tle_handler(elements)
                sleep(300.0)
            except Exception as inst:
                print type(inst)     # the exception instance
                print inst.args      # arguments stored in .args
                print inst           # __str__ allows args to be printed directly
