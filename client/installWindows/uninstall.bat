echo off
echo:
echo THIS WILL UNINSTALL EVERY PROGRAM AND DEPENDENCY USED IN THE PROGRAM.
echo:
echo IF YOU WISH TO KEEP SOME SOFTWARE, MAKE SURE YOU DECLINE THE UNINSTALL PROCESS OF THE SPECIFIC SOFTWARE YOU WISH TO KEEP
echo:

pip uninstall requests
pip uninstall keyboard
pip uninstall stdiomask
pip uninstall termcolor

del ..\launch.bat
