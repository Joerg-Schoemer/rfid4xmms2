from logging import debug
from os import environ


class Config(object):
    COMMANDS_DIR = environ.get('COMMANDS_DIR') or './commands'
    MEDIA_LIB = environ.get('MEDIA_LIB') or './music'
    SCRIPTS_DIR = environ.get('SCRIPTS_DIR') or './scripts'
    SECRET_KEY = environ.get('SECRET_KEY') or 'you-will-never-guess'
    SOUNDS_DIR = environ.get('SOUNDS_DIR') or './sounds'
    UNKNOWN_DIR = environ.get('UNKNOWN_DIR') or './unknown'

    def __init__(self):
        debug("COMMANDS_DIR: %s" % self.COMMANDS_DIR)
        debug("MEDIA_LIB: %s" % self.MEDIA_LIB)
        debug("SCRIPTS_DIR: %s" % self.SCRIPTS_DIR)
        debug("SECRET_KEY: %s" % self.SECRET_KEY)
        debug("SOUNDS_DIR: %s" % self.SOUNDS_DIR)
        debug("UNKNOWN_DIR: %s" % self.UNKNOWN_DIR)
