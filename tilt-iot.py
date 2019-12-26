#/usr/bin/env python3
#
# Joe Richards
# nospam-github at disonformity.net
# 2019-12-26
#

from tilt import Tilt, TiltScanner
import sys
import logging

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')

t = TiltScanner(config='tilt-iot-config.yaml')
t.scan()
