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
    def __init__(self, threadID, name, sendflag, ser):
        threading.Thread.__init__(self)
        self.__mutex = threading.Lock()
        self.threadID = threadID
        self.__name = name
        self.config = config.config
        self.sendflag = sendflag
        self.ser = ser

    def __connect__(self):
        #print((self.config))
        self.__mqtt_id = str(math.floor(time.time() + self.sendflag))
        #print(self.__mqtt_id);
        self.__mqtt__ = mqtt.Client(self.__mqtt_id)
        self.__mqtt__.username_pw_set(self.config["username"], self.config["passwd"])
        self.__mqtt__.on_connect = self.on_connect
        self.__mqtt__.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        #print("Connected with result code "+str(rc))
        try :
            client.subscribe("computex/" + self.config["city"] + "/iot/" + self.config["gateway_id"]  + "/backend")
        except :
            print("subscribe error")
        else:
            print("subscribe ok")


    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("disconect start")
            self.try_connect()
            print("disconect stop")
            time.sleep(2)

    def on_message(self, client, userdata, msg):
        ctrl_data = [0x1, 0x0, 0x0]
        js_code = json.loads(msg.payload.decode('utf8'))

        if "gateway_id" in js_code :
            ctrl_data[1] = js_code["funcode"]
            ctrl_data[2] = js_code["value"]
            #print(ctrl_data)

            #self.__mutex.acquire()
            self.ser.write(ctrl_data)
            #self.__mutex.release()

    def recv_mqttmsg(self):
        self.__mqtt__.on_message = self.on_message
        self.try_connect();
        self.__mqtt__.loop_forever()

    def try_connect(self):
        while True:
            try :
                print("connect start")
                self.__mqtt__.connect(self.config["wss_addr"], 1883)
                print(self.sendflag)
            except :
                print("connect error")
                time.sleep(2)
            else:
                print("connect success")
                break

    def send_mqttmsg(self):
        self.try_connect()

        while True :
            #self.__mutex.acquire()
            self.recvmsg = self.ser.read(size = 4)
            self.ser.reset_input_buffer()
            #self.__mutex.release()

            if len(self.recvmsg) == 4 :
                send_msg["funcode"] = self.recvmsg[1]
                send_msg["gateway_id"] = self.config["gateway_id"]
                if self.recvmsg[1] == 4 :
                    send_msg["value"] = self.recvmsg[2] + (self.recvmsg[3] / 10)
                else :
                    send_msg["value"] = self.recvmsg[2]

                #print(send_msg)
                try :
                    self.__mqtt__.publish("computex/" + self.config["city"] + "/iot/" + self.config["gateway_id"] + "/DataTransfer", json.dumps(send_msg))
                except :
                    print("publish error")

    def run(self):
        self.__connect__()
        if self.sendflag :
            self.recv_mqttmsg()
        else:
            self.send_mqttmsg();

if __name__ == '__main__':
    ser_config = serial_port()

    ser = serial.Serial(ser_config.config["port"], ser_config.config["baudrate"])

    mqtt_recv = mqtt_datatranslate(1, "mqtt_recv_thread", 1, ser);
    mqtt_send = mqtt_datatranslate(2, "mqtt_send_thread", 0, ser);

    mqtt_recv.start()
    mqtt_send.start()

    mqtt_recv.join()
    mqtt_send.join()

    ser.close()
