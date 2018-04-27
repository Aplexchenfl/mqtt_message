#!/usr/bin/python3

import configparser
import threading
import os
import json
import time

class configure(threading.Thread):

    __muxtex = threading.Lock();
    __configure_file_path = "config/config.json";

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, "_inst"):

            cls._inst = super(configure, cls).__new__(cls);
            json_data = open(cls.__configure_file_path);
            cls.config = json.load(json_data);

        return cls._inst;

    def print_cfg(cls):
        print(cls.config);
        print(cls.config["device"]);
        print(cls.config["username"]);
        print(cls.config["wss_addr"]);
        print(cls.config["passwd"]);
        print(cls.config["wss_port"]);

    def set_file_path(cls, filepath):
        cls.__configure_file_path = filepath;

config = configure();

if __name__ == '__main__':
    config.set_file_path("config/config.json");
    config.print_cfg();
