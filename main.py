#!/usr/bin/env python3

import logging
import signal
from multiprocessing import Process

from rfid4xmms2 import application
from rfid4xmms2.observer import doit, end_read, handle_hup

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    application.logger.info('starting...')
    observer_process = Process(target=doit)
    observer_process.start()
    signal.signal(signal.SIGINT, end_read)
    signal.signal(signal.SIGHUP, handle_hup)
    application.run(host='0.0.0.0', debug=False)
