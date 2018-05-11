#!/usr/bin/python3

from mqtt_datatransfer.mqtt_DataTransfer import *
import paho.mqtt.client as mqtt
import time
import json
from config.config import *
import threading
from serial_py.serial_test import *
import serial


if __name__ == '__main__':
    ser_config = serial_port()

    ser = serial.Serial(ser_config.config["port"], ser_config.config["baudrate"])

    mqtt_thread = mqtt_run("mqtt_thread", ser)

    mqtt_thread.start()

    mqtt_thread.join()

    ser.close()
