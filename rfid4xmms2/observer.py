import logging
import sys
import time
from os.path import join
from pathlib import Path

from pirc522 import RFID
from pygame import mixer

from rfid4xmms2 import config
from rfid4xmms2.xmms2 import Xmms2Ctl

xmms2ctl = Xmms2Ctl(config.SCRIPTS_DIR, config.COMMANDS_DIR)
run = True
reader = RFID()
last_command_file_name = None
logger = logging.getLogger(__name__)


def play_sound(_file):
    if not mixer.get_init():
        mixer.init()
    mixer.music.load(_file)
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(0.2)


def play_error_sound():
    play_sound(join(config.SOUNDS_DIR, 'no.mp3'))


def play_success_sound():
    play_sound(join(config.SOUNDS_DIR, 'yes.mp3'))


def generate_command_file_name(_card_name):
    return join(config.COMMANDS_DIR, _card_name)


def generate_file_name(_uid):
    return '_'.join("{:02X}".format(i) for i in _uid) + '.cmd'


def set_last_command_file_name(_file):
    global last_command_file_name
    last_command_file_name = _file


def command_file_name_not_changed(_command_file_name):
    return last_command_file_name == _command_file_name


def create_unknown_file(_card_name):
    file_name = join(config.UNKNOWN_DIR, _card_name)
    Path(file_name).touch()


def doit():
    global run
    play_success_sound()
    while run:
        last_read_time = time.time()
        time.sleep(0.1)
        reader.wait_for_tag()

        (error, data) = reader.request()
        if error:
            set_last_command_file_name(None)
            continue

        (error, uid) = reader.anticoll()
        if error:
            set_last_command_file_name(None)
            continue

        card_name = generate_file_name(uid)
        logger.info('card_name %s', card_name)
        command_file_name = generate_command_file_name(card_name)
        if time.time() - last_read_time < 0.5 and command_file_name_not_changed(command_file_name):
            continue

        if not Path(command_file_name).is_file():
            logger.info('command file \'%s\' not found', command_file_name)
            create_unknown_file(card_name)
            play_error_sound()
            set_last_command_file_name(command_file_name)
            continue

        set_last_command_file_name(command_file_name)

        play_card = xmms2ctl.play_card(card_name)
        if play_card is not None and not play_card:
            play_error_sound()
            continue

        play_success_sound()
        if play_card is not None and play_card:
            xmms2ctl.start()


def end_read(signum, frame):
    global run
    logger.info('\nCtrl+C captured, ending read.')
    run = False
    reader.cleanup()
    xmms2ctl.pause()
    sys.exit(0)


def handle_hup(signum, frame):
    logger.warning('SIGHUP received')
