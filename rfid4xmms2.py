#!/usr/bin/env python3

import signal
import time
import datetime
import sys
import subprocess
import pygame

from pirc522 import RFID
from pathlib import Path

root = "/home/pi/rfid4xmms2"
commandsFolder = '{}/commands/'.format(root)
unknownFolder = '{}/unknown/'.format(root)
soundsFolder = '{}/sounds/'.format(root)

run = True
rdr = RFID()

lastCommandFileName = None
allowedCommands = ['next', 'prev', 'pause', 'play', 'stop', 'toggle', 'album', 'title', 'url', 'volume', 'advent']


def logging(message):
    print(message)
    sys.stdout.flush()


def play_sound(file):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.2)


def play_error_sound():
    play_sound(soundsFolder + 'no.mp3')


def play_success_sound():
    play_sound(soundsFolder + 'yes.mp3')


def xmms2cmd(cmd):
    subprocess.run(['su', 'pi', '-c xmms2 ' + cmd])


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


def play_url(url):
    xmms2cmd('stop')
    xmms2cmd('clear')
    xmms2cmd('add ' + url)
    xmms2cmd('play')


def play_advent(album):

    today = datetime.date.today()
    if today.month == 12:
        todaysDay = str(today.day).zfile(2)
        xmms2cmd('stop')
        xmms2cmd('clear')
        xmms2cmd('add \'album:' + album + ' AND title:' + todaysDay + '\'')
        xmms2cmd('play')
    else:
        play_album(album)


def volume(direction):
    if direction == 'up':
        xmms2cmd('server volume +10')
    elif direction == 'down':
        xmms2cmd('server volume -10')
    else:
        logging('invalid direction value \'' + direction + '\'')
        play_error_sound()


def generate_command_file_name(uid):
    return commandsFolder + generate_file_name(uid)


def generate_file_name(uid):
    return '_'.join("{:02X}".format(i) for i in uid) + '.cmd'


def set_last_command_file_name(file):
    global lastCommandFileName
    lastCommandFileName = file


def command_file_name_not_changed(commandFileName):
    return lastCommandFileName == commandFileName


def end_read(signal, frame):
    global run
    logging("\nCtrl+C captured, ending read.")
    run = False
    rdr.cleanup()
    xmms2cmd('stop')
    sys.exit()


def handle_hup(signal, frame):
    logging("SIGHUP received")


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

    commandFileName = generate_command_file_name(uid)

    if time.time() - lastReadTime < 0.5 and command_file_name_not_changed(commandFileName):
        continue

    cmdFilePath = Path(commandFileName)
    if not cmdFilePath.is_file():
        logging('command file \'' + commandFileName + '\' not found')
        # creating unknown file
        Path(unknownFolder + generate_file_name(uid)).touch()
        play_error_sound()
        set_last_command_file_name(commandFileName)
        continue

    with open(commandFileName) as file:
        cmdAction = file.readline().strip()
        if cmdAction not in allowedCommands:
            logging('command \'' + cmdAction + '\' not allowed')
            play_error_sound()
            set_last_command_file_name(commandFileName)
            continue

        play_success_sound()
        if cmdAction == 'album':
            albumPattern = file.readline().strip()
            play_album(albumPattern)
            logging('playing album ' + albumPattern)
        elif cmdAction == 'advent':
            albumPattern = file.readline().strip()
            play_advent(albumPattern)
            logging('playing advent album ' + albumPattern)
        elif cmdAction == 'title':
            titlePattern = file.readline().strip()
            play_title(titlePattern)
            logging('playing title ' + titlePattern)
        elif cmdAction == 'url':
            url = file.readline().strip()
            play_url(url)
            logging('playing url ' + url)
        elif cmdAction == 'volume':
            direction = file.readline().strip()
            volume(direction)
            logging('executing \'' + cmdAction + '\'' + ' direction=\'' + direction + '\'')
        else:
            xmms2cmd(cmdAction)
            logging('executing \'' + cmdAction + '\'')

    set_last_command_file_name(commandFileName)
