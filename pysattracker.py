#!/usr/bin/python2

import json
import threading
from time import sleep
import sys
import logging
import logging.handlers
import argparse
import signal

from track import Track
from nettle import NetTle
from location import Location


parser = argparse.ArgumentParser(description='Satellite Antenna Tracker')
parser.add_argument('-c', '--config', dest='config', default='/etc/pysattracker.json', help='Config file')
parser.add_argument('-s', '--syslog', action='store_true', help='Syslog logging')
parser.add_argument('-v', '--verbose', action='store_true', help='Log all')
args = parser.parse_args()

logger = logging.getLogger('pysattracker')
loglevel = logging.DEBUG

if args.verbose:
    logging.DEBUG
else:
    logging.INFO

logger.setLevel(loglevel)

if args.syslog:
    loghandler = logging.handlers.SysLogHandler(address='/dev/log')
    formater = logging.Formatter('pysattracker: %(message)s')
    loghandler.setFormatter(formater)
else:
    loghandler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)+8s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    loghandler.setFormatter(formatter)

logger.addHandler(loghandler)

config = {}

try:
    config = json.load(open(args.config))
except IOError:
    logger.warning("Error: Config file (%s) not found.", args.config)


def tle_cb(elements):
    st.set_elements(elements)


def location_cb(latitude, longitude, altitude):
    st.set_location(latitude, longitude, altitude)
    logger.info("location received. %s %s %s", latitude, longitude, altitude)


def start_tracker():
    # homeargs = {
    #    'lat': config['home']['lat'],
    #    'lng': config['home']['lng'],
    #    'alt': config['home']['alt'],
    # }
    while True:
        sleep(5)


logger.info("Starting pysattracker")

st = Track(config)
tles = NetTle(tle_cb, config)
location = Location(location_cb, config)


def signal_handler(signal, frame):
    logger.info("Stopping pysattracker")
    st.exit()
    tles.exit()
    location.exit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Start tracker in main thread
start_tracker()
