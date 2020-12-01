#!/usr/bin/env python3

import signal
import time
import datetime
import sys
import subprocess
import pygame
import grp
import pwd
import logging
import os

from pirc522 import RFID
from pathlib import Path

logging.basicConfig(level=logging.INFO)

root = "/home/pi/rfid4xmms2"
commands_folder = '{}/commands/'.format(root)
unknown_folder = '{}/unknown/'.format(root)
sounds_folder = '{}/rfid4xmms2/sounds/'.format(root)

run = True
rdr = RFID()

last_command_file_name = None
allowedCommands = ['next', 'prev', 'pause', 'play', 'stop', 'toggle', 'album', 'title', 'url', 'volume', 'advent']


def play_sound(_file):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    pygame.mixer.music.load(_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.2)


def play_error_sound():
    play_sound(sounds_folder + 'no.mp3')


def play_success_sound():
    play_sound(sounds_folder + 'yes.mp3')


def xmms2cmd(cmd):
    logging.info(cmd)
    subprocess.run(['su', 'pi', '-c xmms2 ' + cmd], check=True)


def play_album(pattern):
    xmms2cmd('stop')
    xmms2cmd('clear')
    xmms2cmd('add -o partofset,tracknr album:' + pattern)
    xmms2cmd('play')


def play_title(pattern):
    xmms2cmd('stop')
    xmms2cmd('clear')
    xmms2cmd('add title:' + pattern)
    xmms2cmd('play')


def play_url(_url):
    xmms2cmd('stop')
    xmms2cmd('clear')
    xmms2cmd('add ' + _url)
    xmms2cmd('play')


def play_advent(pattern):
    today = datetime.date.today()
    if today.month == 12 and today.day <= 24:
        xmms2cmd('stop')
        xmms2cmd('clear')
        xmms2cmd('add album:' + pattern + ' AND tracknr:' + today.day)
        xmms2cmd('play')
    else:
        play_album(pattern)


def volume(_direction):
    if _direction == 'up':
        xmms2cmd('server volume +10')
    elif _direction == 'down':
        xmms2cmd('server volume -10')
    else:
        logging.warning('invalid direction value \'' + _direction + '\'')
        play_error_sound()


def generate_command_file_name(_uid):
    return commands_folder + generate_file_name(_uid)


def generate_file_name(_uid):
    return '_'.join("{:02X}".format(i) for i in _uid) + '.cmd'


def set_last_command_file_name(_file):
    global last_command_file_name
    last_command_file_name = _file


def command_file_name_not_changed(_command_file_name):
    return last_command_file_name == _command_file_name


def end_read():
    global run
    logging.info("\nCtrl+C captured, ending read.")
    run = False
    rdr.cleanup()
    xmms2cmd('stop')
    sys.exit()


def handle_hup():
    logging.debug("SIGHUP received")


def create_unknown_file(_uuid):
    file_name = unknown_folder + generate_file_name(_uuid)
    Path(file_name).touch()
    _uid = pwd.getpwnam('pi').pw_uid
    _gid = grp.getgrnam('pi').pw_gid
    os.chown(file_name, _uid, _gid)


signal.signal(signal.SIGINT, end_read)
signal.signal(signal.SIGHUP, handle_hup)
play_success_sound()
while run:
    lastReadTime = time.time()
    time.sleep(0.1)
    rdr.wait_for_tag()

    (error, data) = rdr.request()
    if error:
        set_last_command_file_name(None)
        continue

    (error, uid) = rdr.anticoll()
    if error:
        set_last_command_file_name(None)
        continue

    command_file_name = generate_command_file_name(uid)
    if time.time() - lastReadTime < 0.5 and command_file_name_not_changed(command_file_name):
        continue

    if not Path(command_file_name).is_file():
        logging.info('command file \'' + command_file_name + '\' not found')
        create_unknown_file(uid)
        play_error_sound()
        set_last_command_file_name(command_file_name)
        continue

    with open(command_file_name) as file:
        cmd_action = file.readline().strip()
        if cmd_action not in allowedCommands:
            logging.info('command \'' + cmd_action + '\' not allowed')
            play_error_sound()
            set_last_command_file_name(command_file_name)
            continue

        play_success_sound()
        if cmd_action == 'album':
            album_pattern = file.readline().strip()
            logging.debug('playing album ' + album_pattern)
            play_album(album_pattern)
        elif cmd_action == 'advent':
            album_pattern = file.readline().strip()
            logging.debug('playing advent album ' + album_pattern)
            play_advent(album_pattern)
        elif cmd_action == 'title':
            title_pattern = file.readline().strip()
            logging.debug('playing title ' + title_pattern)
            play_title(title_pattern)
        elif cmd_action == 'url':
            url = file.readline().strip()
            logging.debug('playing url ' + url)
            play_url(url)
        elif cmd_action == 'volume':
            direction = file.readline().strip()
            logging.debug('executing \'' + cmd_action + '\'' + ' direction=\'' + direction + '\'')
            volume(direction)
        else:
            logging.debug('executing \'' + cmd_action + '\'')
            xmms2cmd(cmd_action)
    set_last_command_file_name(command_file_name)
