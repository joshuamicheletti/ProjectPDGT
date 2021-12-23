#!/bin/bash
sudo pip uninstall keyboard
sudo pip uninstall stdiomask
sudo pip uninstall termcolor
sudo apt remove python3-tk

sudo apt-get update
sudo python3 -m pip uninstall pip
sudo apt-get remove python3-setuptools

