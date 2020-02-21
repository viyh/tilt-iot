#/usr/bin/env python3
#
# Joe Richards
# nospam-github at disonformity.net
# 2019-12-26
#

from beacontools import BeaconScanner, IBeaconFilter
import time
import logging
from statistics import mean
import yaml
import json

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

TILTS = {
    'a495bb10-c5b1-4b44-b512-1370f02d74de': 'Red',
    'a495bb20-c5b1-4b44-b512-1370f02d74de': 'Green',
    'a495bb30-c5b1-4b44-b512-1370f02d74de': 'Black',
    'a495bb40-c5b1-4b44-b512-1370f02d74de': 'Purple',
    'a495bb50-c5b1-4b44-b512-1370f02d74de': 'Orange',
    'a495bb60-c5b1-4b44-b512-1370f02d74de': 'Blue',
    'a495bb70-c5b1-4b44-b512-1370f02d74de': 'Yellow',
    'a495bb80-c5b1-4b44-b512-1370f02d74de': 'Pink',
}

class TiltScanner():
    def __init__(self, config=None):
        self.logger = logging.getLogger('tilt-iot.tilt.TiltScanner')
        self.logger.info('Initializing TiltScanner')
        self.parse_config(config)
        self.tilts = {}
        self.iot = self.iot_connect()

    def parse_config(self, config):
        if not config:
            return False
        with open(config, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
        self.scan_interval = cfg.get('bluetooth.scan_interval', 5)
        self.scan_pause = cfg.get('bluetooth.scan_pause', 20)
        self.scan_mode = cfg.get('bluetooth.scan_mode', 0)
        self.iot_client = cfg.get('iot.client', 'pi')
        self.iot_topic = cfg.get('iot.topic', 'brewing/{}'.format(self.iot_client))
        self.iot_endpoint = cfg.get('iot.endpoint', None)
        self.iot_ca_cert = cfg.get('iot.credential_ca_cert', None)
        self.iot_key = cfg.get('iot.credential_key', None)
        self.iot_cert = cfg.get('iot.credential_cert', None)
        self.sg_as_int = cfg.get('values.sg_as_int', True)
        return True

    def scan(self):
        tilt_filter = [IBeaconFilter(uuid=TILT) for TILT in TILTS.keys()]
        while True:
            try:
                scanner = BeaconScanner(self.callback, device_filter=tilt_filter)
                scanner.start()
                time.sleep(self.scan_interval)
                scanner.stop()
                self.submit_metrics()
                time.sleep(self.scan_pause)
            except Exception as e:
                self.logger.error(e)
                pass

    def set_tilt(self, uuid, temp_f, sg):
        if not self.sg_as_int:
            sg = sg / 1000.0
        if not uuid in self.tilts or self.scan_mode == 2:
            self.tilts[uuid] = Tilt(uuid)
        if self.scan_mode == 1 and self.tilts[uuid].temp_f and self.tilts[uuid].sg:
            return True
        self.logger.debug("Tilt: {}, Temperature F: {}, Specific Gravity: {}".format(
                TILTS[uuid],
                temp_f,
                sg
            )
        )
        self.tilts[uuid].add_temp(temp_f)
        self.tilts[uuid].add_sg(sg)

    def iot_connect(self):
        MQTTClient = AWSIoTMQTTClient(self.iot_client)
        MQTTClient.configureEndpoint(self.iot_endpoint, 8883)
        MQTTClient.configureCredentials(self.iot_ca_cert, self.iot_key, self.iot_cert)
        MQTTClient.configureOfflinePublishQueueing(-1)
        MQTTClient.configureDrainingFrequency(2)
        MQTTClient.configureConnectDisconnectTimeout(10)
        MQTTClient.configureMQTTOperationTimeout(5)
        MQTTClient.connect()
        return MQTTClient

    def submit_metrics(self):
        for tilt in self.tilts:
            self.logger.info(self.tilts[tilt])
            metric_data = self.get_metric(self.tilts[tilt])
            self.logger.debug("Publishing to IoT [{}]: {}".format(self.iot_topic, json.dumps(metric_data)))
            self.iot.publish(self.iot_topic, json.dumps(metric_data), 0)
        self.tilts = {}

    def get_metric(self, tilt):
        return {
            'state': {
                'reported': {
                    'name': tilt.color(),
                    'temp_f': tilt.temp_f,
                    'sg': tilt.sg
                }
            }
        }

    def callback(self, bt_addr, rssi, packet, additional_info):
        self.logger.debug("Packet found: <%s, %d> %s %s" % (bt_addr, rssi, packet.uuid, additional_info))
        self.set_tilt(packet.uuid, additional_info['major'], additional_info['minor'])

class Tilt():
    def __init__(self, uuid=None):
        self.logger = logging.getLogger('tilt-iot.tilt.Tilt')
        self.uuid = uuid
        self.temps_f = []
        self.sgs = []
        self.temp_f = None
        self.temp_c = None
        self.sg = None

    def __str__(self):
        return "Tilt: {}, temp_f: {}, temp_c: {:.1f}, sg: {}, temps_f: {}, sgs: {}".format(
            self.color(), self.temp_f, self.temp_c, self.sg, self.temps_f, self.sgs)

    def color(self):
        return TILTS[self.uuid]

    def add_temp(self, temp_f):
        self.temps_f.append(temp_f)
        self.temp_f = mean(self.temps_f)
        self.temp_c = round((temp_f - 32) * 5/9, 1)
        return True

    def add_sg(self, sg):
        self.sgs.append(sg)
        self.sg = round(mean(self.sgs))
        return True
