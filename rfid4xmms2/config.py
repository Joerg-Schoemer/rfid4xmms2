import logging
from os import environ

logger = logging.getLogger(__name__)


class Config:

    COMMANDS_DIR = environ.get('COMMANDS_DIR') or './commands'
    MEDIA_LIB = environ.get('MEDIA_LIB') or '../music'
    SCRIPTS_DIR = environ.get('SCRIPTS_DIR') or './scripts'
    SECRET_KEY = environ.get('SECRET_KEY') or 'you-will-never-guess'
    SOUNDS_DIR = environ.get('SOUNDS_DIR') or './sounds'
    UNKNOWN_DIR = environ.get('UNKNOWN_DIR') or './unknown'

    def __init__(self):
        logger.info("COMMANDS_DIR: %s" % self.COMMANDS_DIR)
        logger.info("MEDIA_LIB: %s" % self.MEDIA_LIB)
        logger.info("SCRIPTS_DIR: %s" % self.SCRIPTS_DIR)
        logger.info("SECRET_KEY: %s" % self.SECRET_KEY)
        logger.info("SOUNDS_DIR: %s" % self.SOUNDS_DIR)
        logger.info("UNKNOWN_DIR: %s" % self.UNKNOWN_DIR)
