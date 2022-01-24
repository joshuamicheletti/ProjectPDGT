# ProjectPDGT

Published under GNU GPLv3 license

Web API to handle files devided between servers (buckets).

This tool comes with a small client to access the functionalities of the API, but all the methods are accessible through HTTP requests.

The API runs on Node.js, and is currently hosted on "https://projectpdgt.herokuapp.com".
It uses the following libraries:
- express
- js-sha256
- cookie-parser
- multer
- minio

The client is completely written in Python and uses the following libraries:
- requests
- base64
- re
- os
- keyboard
- sys
- stdiomask
- time
- termcolor
- tkinter
- termos (ubuntu) / msvcrt (windows)


# Install

Windows 10:

- Download the repository (download on github or git clone https://github.com/joshuamicheletti/ProjectPDGT.git).
- Head to ProjectPDGT\client\installWindows
- You will need python for this, which can be installed by downloading the latest python version from the microsoft store, or you can use the "installPython.bat" script to get automatically redirected to the download page, in case you don't already have it
- Run the script "install.bat"
- Head back to ProjectPDGT\client and launch the script "launch.bat" to launch the application

Ubuntu 20.04:

- Download the repository (download on github or git clone https://github.com/joshuamicheletti/ProjectPDGT.git)
- Head to ProjectPDGT/client/installUbuntu
- Run the script "install.sh"
- Head back to ProjectPDGT/client and launch the script "launch.sh" to launch the application

# Uninstall

Windows 10:

This procedure will delete all the dependencies needed for this program to work (requests, keyboard, stdiomask, termcolor)
If you wish to keep any of these, decline the uninstall process when asked.

- Head to ProjectPDGT\client\installWindows
- Run the script "uninstall.bat"
- Choose what you want to keep and what you want to remove when asked
- To uninstall python, head to the microsoft store and uninstall python from there

Ubuntu 20.04:

This procedure will delete all the dependencies needed for this program to work (keyboard, stdiomask, termcolor, python3-tk, pip, python3-setuptools)
If you wish to keep any of these, decline the uninstall process when asked.

- Head to ProjectPDGT/client/installUbuntu
- Run the script "uninstall.sh"
- Choose what you want to keep and what you want to remove when asked
