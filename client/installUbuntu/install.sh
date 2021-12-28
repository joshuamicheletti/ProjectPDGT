#!/bin/bash
sudo apt-get update
sudo apt-get install python3-setuptools
sudo python3 -m easy_install install pip
sudo pip install keyboard
sudo pip install stdiomask
sudo pip install termcolor
sudo apt install python3-tk

sudo python3 program.py
