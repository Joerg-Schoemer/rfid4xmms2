#!/usr/bin/env python3

from rfid4xmms2 import application
from multiprocessing import Process
from rfid4xmms2.observer import doit


if __name__ == '__main__':
    observer_process = Process(target=doit)
    observer_process.start()
    application.run()
