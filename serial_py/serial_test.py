#!/usr/bin/python3

import json
import serial
import threading
import time

class serial_port():
    __configure_file_path = "serial_py/config.json"

    def __init__(self):
        json_data = open(self.__configure_file_path);
        self.config = json.load(json_data)

    def print_msg(self):
        print(self.config)
        print(self.config["port"])
        print(self.config["baudrate"])
        print(self.config["bytesize"])
        print(self.config["stopbits"])
        print(self.config["parity"])
        print(self.config["timeout"])

data = [0x1, 0x3, 0x3]

class Datatranslate(threading.Thread):
    def __init__(self, threadID, name, msg, ser, readflag):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.msg = msg
        self.ser = ser
        self.readflag = readflag;
    def run(self):

        if self.readflag :
            self.ser_recvmsg()
        else:
            self.ser_writemsg()

    def ser_writemsg(self):
        i = 0
        while 1:
            time.sleep(1)
            data[2] = (data[2] + 1) % 10
            ser_Lock.acquire()
            self.ser.write(data)
            ser_Lock.release()

    def ser_recvmsg(self):
        while 1:
            ser_Lock.acquire()
            self.recvmsg = ser.read(size = 3)
            ser_Lock.release()

            if (len(self.recvmsg) == 3):
                print("device_id : " + self.recvmsg[0])
                print("funcode : " + self.recvmsg[1])
                print("value : " + self.recvmsg[2])
            time.sleep(1)

ser_Lock = threading.Lock();

if __name__ == '__main__':
    ser_config = serial_port();
    ser_config.print_msg();

    ser = serial.Serial(ser_config.config["port"], ser_config.config["baudrate"], timeout = ser_config.config["timeout"])

    #ser.write(("hello").encode());

    read_pthread = Datatranslate(1, "read_pthread", "hello\n", ser, 1)
    write_pthread = Datatranslate(2, "write_pthread", "hello\n", ser, 0)

    read_pthread.start();
    write_pthread.start();
    read_pthread.join();
    write_pthread.join();

    while 1:
        pass;
        time.sleep(10);

    ser.close();

    pass;
