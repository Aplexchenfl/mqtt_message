#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
import json
from config.config import *
import threading
from serial_py.serial_test import *
import serial
import math

send_msg = {
        'device_id': 1,
        'funcode': 3,
        'value': 0,
        'gateway_id': '5100'
        }

class mqtt_datatranslate(threading.Thread):
    def __init__(self, name, ser):
        threading.Thread.__init__(self)
        self.__mutex = threading.Lock()
        self.__name = name
        self.config = config.config
        self.ser = ser
        self.init_connect()

    def init_connect(self):
        self.__mutex.acquire()
        self.__mqtt_id = str(math.floor(time.time()))
        self.__mqtt__ = mqtt.Client(self.__mqtt_id)
        self.__mqtt__.username_pw_set(self.config["username"], self.config["passwd"])
        self.__mqtt__.on_connect = self.on_connect
        self.__mqtt__.on_disconnect = self.on_disconnect
        self.__mqtt__.on_message = self.sendmsg_to_ser
        self.__mutex.release()

        self.try_connect_to_mqtthub()

    def on_connect(self, client, userdata, flags, rc):
        try :
            client.subscribe("computex/" + self.config["city"] + "/iot/" + self.config["gateway_id"]  + "/ledBackend")
            client.subscribe("computex/" + self.config["city"] + "/iot/" + self.config["gateway_id"]  + "/numBackend")
        except :
            print("subscribe error")
        else:
            print("subscribe ok")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("disconect start")
            self.try_connect_to_mqtthub()
            print("disconect stop")
            time.sleep(2)

    def sendmsg_to_ser(self, client, userdata, msg):
        ctrl_data = [0x1, 0x0, 0x0]
        js_code = json.loads(msg.payload.decode('utf8'))

        if "gateway_id" in js_code :
            ctrl_data[1] = js_code["funcode"]
            ctrl_data[2] = js_code["value"]
            #print(ctrl_data)

            self.ser.write(ctrl_data)

    def sendmsg_to_mqtthub(self, send_msg):
        if send_msg["funcode"] == 1 :
            chat = "computex/" + self.config["city"] + "/iot/" + self.config["gateway_id"] + "/btnData"
        elif send_msg["funcode"] == 4 :
            chat = "computex/" + self.config["city"] + "/iot/" + self.config["gateway_id"] + "/tempData"
        else :
            pass

        self.__mqtt__.publish(chat, payload = json.dumps(send_msg), retain = True)

    def try_connect_to_mqtthub(self):
        while True:
            try :
                print("connect start")
                self.__mqtt__.connect(self.config["wss_addr"], 1883)
            except :
                print("connect error")
                time.sleep(2)
            else:
                print("connect success")
                break

    def run(self):
        self.__mqtt__.loop_forever()


class mqtt_run(threading.Thread):
    def __init__(self, name, ser):
        threading.Thread.__init__(self)
        self.ser = ser
        self.name = name
        self.Mqtt_Datatranslate = mqtt_datatranslate(name, ser)
        self.Mqtt_Datatranslate.start()
        #self.Mqtt_Datatranslate.join()

    def run(self):
        while True :
            self.recvmsg = self.ser.read(size = 4)
            self.ser.reset_input_buffer()

            if len(self.recvmsg) == 4 :
                send_msg["funcode"] = self.recvmsg[1]
                send_msg["gateway_id"] = config.config["gateway_id"]
                if self.recvmsg[1] == 4 :
                    send_msg["value"] = self.recvmsg[2] + (self.recvmsg[3] / 10)
                else :
                    send_msg["value"] = self.recvmsg[2]

                self.Mqtt_Datatranslate.sendmsg_to_mqtthub(send_msg)


if __name__ == '__main__':
    ser_config = serial_port()

    ser = serial.Serial(ser_config.config["port"], ser_config.config["baudrate"])

    mqtt_thread = mqtt_run("mqtt_thread", ser)

    mqtt_thread.start()

    mqtt_thread.join()

    ser.close()
