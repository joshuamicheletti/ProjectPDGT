#!/bin/bash

printf "THIS WILL UNINSTALL EVERY PROGRAM AND DEPENDENCY USED IN THE PROGRAM.\n\nIF YOU WISH TO KEEP SOME SOFTWARE, MAKE SURE YOU DECLINE THE UNINSTALL PROCESS OF THE SPECIFIC SOFTWARE YOU WISH TO KEEP\n\n"

sudo pip uninstall keyboard
sudo pip uninstall stdiomask
sudo pip uninstall termcolor
sudo apt remove python3-tk

sudo apt-get update
sudo python3 -m pip uninstall pip
sudo apt-get remove python3-setuptools

rm ../launch.sh
