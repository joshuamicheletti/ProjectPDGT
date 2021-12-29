#!/bin/bash
sudo apt-get update
sudo apt-get install python3-setuptools
sudo python3 -m easy_install install pip
sudo pip install keyboard
sudo pip install stdiomask
sudo pip install termcolor
sudo apt install python3-tk

echo "#!/bin/bash"> ../launch.sh
echo sudo python3 program.py>> ../launch.sh
chmod a+x ../launch.sh

printf "\nTO RUN THE PROGRAM, HEAD TO 'ProjectPDGT/client' AND RUN 'launch.bat'\n\n"
