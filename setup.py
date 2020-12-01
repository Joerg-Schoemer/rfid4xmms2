#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="rfid4xmms2",
    version="1.0.0",
    author="Schömer, Jörg",
    author_email="joerg@joerg-schoemer.de",
    description="control xmms2 on a Raspberry PI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Joerg-Schoemer/rfid4xmms2",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    package_data={
        "rfid4xmms2": ["sounds/*.mp3"],
    }
)
