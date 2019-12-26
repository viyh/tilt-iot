# tilt-iot
Tilt Hydrometer data logging via AWS IoT

## Installation

* Allow non-root users to run the BLE scanner:
```sudo setcap cap_net_raw+eip /usr/bin/python3.5```
```sudo apt-get install -y python3-pip python3-bluez gcc libbluetooth-dev libcap2-bin```
```pip3 install -r requirements.txt```

## Setup

* Create AWS Account and deploy cloudformation-iot-lambda.yaml CloudFormation Stack. Make sure to setup the correct Brewer's Friend URL in the CloudFormation stack parameter.
* Copy the tilt-iot-config.defaults.yaml file to tilt-iot-config.yaml and customize any values necessary.
* Create your AWS IoT thing credentials and set the credential file (key, cert, CA cert) locations, name, and endpoint in tilt-iot-config.yaml.

## Run

```python3 tilt-iot.py```
