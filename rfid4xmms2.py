#!/usr/bin/env python3

import signal
import time
import sys
import subprocess
import pygame

from pirc522 import RFID
from pathlib import Path

root="/home/pi/rfid4xmms2"
commandsFolder = '{}/commands/'.format(root)
soundsFolder = '{}/sounds/'.format(root)

run = True
rdr = RFID()

lastCommandFileName = None
allowedCommands = ['next', 'prev', 'pause', 'play', 'stop', 'toggle', 'album', 'title', 'url', 'volume']

def logging(message):
    print(message)
    sys.stdout.flush()

def playSound(file):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.2)

def playErrorSound():
    playSound(soundsFolder + 'no.mp3')

def playSuccessSound():
    playSound(soundsFolder + 'yes.mp3')

def xmms2cmd(cmd):
    subprocess.run(['su', 'pi', '-c xmms2 ' + cmd])

def playAlbum(pattern):
    xmms2cmd('stop')
    xmms2cmd('clear')
    xmms2cmd('add -o tracknr album:' + pattern)
    xmms2cmd('play')

def playTitle(pattern):
    xmms2cmd('stop')
    xmms2cmd('clear')
    xmms2cmd('add title:' + pattern)
    xmms2cmd('play')

def playUrl(url):
    xmms2cmd('stop')
    xmms2cmd('clear')
    xmms2cmd('add ' + url)
    xmms2cmd('play')

def volume(direction):
    if direction == 'up':
        xmms2cmd('server volume +10')
    elif direction == 'down':
        xmms2cmd('server volume -10')
    else:
        logging('invalid direction value \'' + direction + '\'')
        playErrorSound()

def generateCommandFileName(uid):
    return commandsFolder + '_'.join("{:02X}".format(i) for i in uid) + '.cmd'

def setLastCommandFileName(file):
    global lastCommandFileName
    lastCommandFileName = file

def commandFileNameNotChanged(commandFileName):
    return lastCommandFileName == commandFileName

def end_read(signal,frame):
    global run
    logging("\nCtrl+C captured, ending read.")
    run = False
    rdr.cleanup()
    xmms2cmd('stop')
    sys.exit()

def handle_hup(signal,frame):
    logging("SIGHUP received")

signal.signal(signal.SIGINT, end_read)

signal.signal(signal.SIGHUP, handle_hup)

playSuccessSound()

while run:
    lastReadTime = time.time()
    time.sleep(0.1)
    rdr.wait_for_tag()

    (error, data) = rdr.request()
    if error:
        setLastCommandFileName(None)
        continue

    (error, uid) = rdr.anticoll()
    if not error:
        commandFileName = generateCommandFileName(uid)

        if time.time() - lastReadTime < 0.5 and commandFileNameNotChanged(commandFileName):
            continue

        cmdFilePath = Path(commandFileName)
        if not cmdFilePath.is_file():
            logging('command file \'' + commandFileName + '\' not found')
            playErrorSound()
            setLastCommandFileName(commandFileName)
            continue

        with open(commandFileName) as f:
            cmd = f.readline().strip()
            if not cmd in allowedCommands:
                logging('command \'' + cmd + '\' not allowed')
                playErrorSound()
                setLastCommandFileName(commandFileName)
                continue

            playSuccessSound()
            if cmd == 'album':
                albumPattern = f.readline().strip()
                playAlbum(albumPattern)
                logging('playing album ' + albumPattern)
            elif cmd == 'title':
                titlePattern = f.readline().strip()
                playTitle(titlePattern)
                logging('playing title ' + titlePattern)
            elif cmd == 'url':
                url = f.readline().strip()
                playUrl(url)
                logging('playing url ' + url)
            elif cmd == 'volume':
                direction = f.readline().strip()
                volume(direction)
                logging('executing \'' + cmd +'\'' + ' direction=\'' + direction + '\'')
            else:
                xmms2cmd(cmd)
                logging('executing \'' + cmd +'\'')
        setLastCommandFileName(commandFileName)
    else:
        setLastCommandFileName(None)
