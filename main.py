#!/usr/bin/env python3

import logging
from multiprocessing import Process

from rfid4xmms2 import application
from rfid4xmms2.observer import doit

logging.basicConfig(level=logging.DEBUG)
print('name on main %s' % __name__)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('starting...')
    observer_process = Process(target=doit)
    observer_process.start()
    application.run(host='0.0.0.0', debug=False)
