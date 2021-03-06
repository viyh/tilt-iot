# tilt-iot
Tilt Hydrometer data logging via AWS IoT

## Architecture
![Overview](https://github.com/viyh/tilt-iot/raw/master/tilt-iot.png "Architecture Overview")

## Installation
* Allow non-root users to run the BLE scanner:
```
sudo setcap cap_net_raw+eip /usr/bin/python3.5
```

* Clone this repo:
```
cd /home/pi && git clone git@github.com:viyh/tilt-iot.git
```

* Install dependencies:
```
sudo apt-get install -y python3-pip python3-bluez python3-yaml gcc libbluetooth-dev libcap2-bin git
pip3 install -r requirements.txt
```

## Setup
* Create AWS Account and deploy cloudformation-iot-lambda.yaml CloudFormation Stack. Make sure to setup the correct Brewer's Friend URL in the CloudFormation stack parameter.
* Copy the tilt-iot-config.defaults.yaml file to tilt-iot-config.yaml and customize any values necessary.
* Create your AWS IoT thing credentials and set the credential file (key, cert, CA cert) locations, name, and endpoint in tilt-iot-config.yaml.
* Import grafana_dashboard.json to Grafana (one dashboard per Tilt), and set the dashboard variables as needed.

## Run
```
python3 tilt-iot.py
```
