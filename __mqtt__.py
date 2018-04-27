#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
import json
from config.config import *
import threading
from serial_py.serial_test import *
import serial

send_msg = {
        'device_id': 1,
        'funcode': 3,
        'value': 0,
        'gateway_id': '5100'
        }

class mqtt_datatranslate(threading.Thread):
    def __init__(self, threadID, name, sendflag, ser):
        threading.Thread.__init__(self)
        self.__mutex = threading.Lock()
        self.threadID = threadID
        self.__name = name
        self.config = config.config
        self.sendflag = sendflag
        self.ser = ser
        self.__connect__()

    def __connect__(self):
        #print((self.config))
        self.__mqtt_id = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #print(self.client_id);
        self.__mqtt__ = mqtt.Client(self.__mqtt_id)
        self.__mqtt__.username_pw_set(self.config["username"], self.config["passwd"])
        self.__mqtt__.on_connect = self.on_connect

    def on_connect(self, client, userdata, flags, rc):
        #print("Connected with result code "+str(rc))
        client.subscribe("computex/iot/" + str(self.config["device"])  + "/backend")

    def on_message(self, client, userdata, msg):
        ctrl_data = [0x1, 0x0, 0x0]
        js_code = json.loads(msg.payload.decode('utf8'))

        if "gateway_id" in js_code :
            ctrl_data[1] = js_code["funcode"]
            ctrl_data[2] = js_code["value"]
            #print(ctrl_data)

            self.__mutex.acquire()
            self.ser.write(ctrl_data)
            self.__mutex.release()

    def recv_mqttmsg(self):
        self.__mqtt__.on_message = self.on_message
        self.__mqtt__.connect(self.config["wss_addr"], 1883)
        self.__mqtt__.loop_forever()

    def send_mqttmsg(self):
        while True :

            self.__mutex.acquire()
            self.recvmsg = self.ser.read(size = 3)
            self.__mutex.release()

            if len(self.recvmsg) == 3 :
                send_msg["funcode"] = self.recvmsg[1]
                send_msg["value"] = 1 << (self.recvmsg[2] - 1)

                #print(send_msg)
                self.__mqtt__.connect(self.config["wss_addr"], 1883)
                self.__mqtt__.publish("computex/iot/" + str(self.config["device"])  +  "/DataTransfer", json.dumps(send_msg))
            time.sleep(1)

    def run(self):
        if self.sendflag :
            self.recv_mqttmsg()
        else:
            self.send_mqttmsg();

if __name__ == '__main__':
    ser_config = serial_port()

    ser = serial.Serial(ser_config.config["port"], ser_config.config["baudrate"], timeout = ser_config.config["timeout"])

    mqtt_recv = mqtt_datatranslate(1, "mqtt_recv_thread", 1, ser);
    mqtt_send = mqtt_datatranslate(2, "mqtt_send_thread", 0, ser);

    mqtt_recv.start()
    mqtt_send.start()

    mqtt_recv.join()
    mqtt_send.join()

    ser.close()
