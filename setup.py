#!/usr/bin/env python

from distutils.core import setup

setup(
    name='rfid4xmms2',
    version='1.0',
    description='A project to control xmms2 on a Raspberry PI with an rc522 rfid reader',
    author='Jörg Schömer',
    author_email='joerg@joerg-schoemer.de',
    url='https://github.com/Joerg-Schoemer/rfid4xmms2',
    requires=['pygame', 'pi-rc522']
)
