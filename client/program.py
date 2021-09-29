# LIBRARIES

# library for making HTTP requests
import requests
# library for encoding string to base64
import base64
# library for regular operations
import re
# library for interacting with the OS and running commands
import os
# library for interacting with the keyboard
import keyboard
# library for making system calls
import sys
# library for masking the password inputs
import stdiomask
# library for making wait() calls
import time
# library for writing colored text on the terminal
from termcolor import colored
# library for opening a popup window when asked to open a file
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

# try to import libraries for clearing the input buffer
# by checking weather or not the termios library can imported or not, we can check what operating system we're on
try:
  import sys, termios
  operatingSystem = "linux"
except ImportError:
  import msvcrt
  operatingSystem = "windows"

# set the Tk library to only display the file open window
Tk().withdraw()


# GLOBAL VARIABLES

# url of destination where the webAPI is hosted
url = "https://projectpdgt.herokuapp.com"
# url = "http://localhost:2000"

# variable for keeping track of what server we're logged in
serverCurrent = ""
# variable to store the current password of the server we're logged into
currentServerPassword = ""
# array to store all the names of the available servers
serverList = []
# variable to keep track of what server we're selecting
selectedServer = 0
# boolean variable to keep track of when we need to update the servers list
upToDateServer = False

# variable to store the current username
username = ""
# variable to store the current user password
password = ""
# array to store the files contained in a server
filesList = []
# variable to keep track of what file we're selecting
selectedFile = 0
# boolean variable to keep track of when we need to update the files list
upToDate = True

# variable to keep track of when to listen for keyboard inputs or not
pressed = False
# variable to keep know when we pressed Enter, which means when we're select an option
enter = False

# string to store messages coming from the webAPI
serverMessage = ""

# list of the login commands
loginCommands = ["Login", "Login with Cookie", "Register", "Delete", "Close"]
# variable to keep track of what command to login we're selecting
selectedLoginCommand = 0
# list of the commands within a server
commands = ["Upload File", "Download File", "Delete File", "Change Server", "Delete Server", "Logout", "Close"]
# variable to keep track of what command we're selecting
selectedCommand = 0

# boolean variable to keep track of weather the user is a server owner or not
serverOwner = False


# UTILITY FUNCTIONS

# function to flush the standard input, prevents unwanted input on commands
def flushInput():
  # if the operating system is linux
  if operatingSystem == "linux":
    # flush using this function
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
  # if the operating system is windows
  else:
    # flush using this function
    while msvcrt.kbhit():
      msvcrt.getch()

# function to clear the screen
def clear():
  # if the operating system is linux
  if operatingSystem == "linux":
    # clean the screen using this command
    os.system('clear')
  # if the operating system is windows
  else:
    # clean the screen using this command
    os.system('cls')

# function to read the cookies file
def readCookie():
  # try to open the file to read the cookie
  try:
    cookieFile = open("cookie.txt", "r")
    cookie = cookieFile.read()
    cookieFile.close()
    return(cookie)
  # in case the file doesn't exist or any other error occurs
  except IOError:
    return(False)

# function to encode username and password to base64
def encodeBase64(usernameL, passwordL):
  # check if the username and password to encode exist
  if usernameL != "" and passwordL != "":
    # combine the username and password as: "username:password"
    credentials = usernameL + ":" + passwordL
    # convert the composed string into bytes
    credentials_bytes = credentials.encode('ascii')
    # encode the bytes into base64
    base64_bytes = base64.b64encode(credentials_bytes)
    # convert the bytes into a string again
    base64_message = base64_bytes.decode('ascii')
    # return the final base64 string
    return(base64_message)
  else:
    return(False)

# function to handle keyboard inputs
def keyboardEventHandler(keyboard_event):
    global selectedFile
    global selectedCommand
    global selectedServer
    global pressed
    global enter
    global selectedLoginCommand
    
    # print("Name:", keyboard_event.name)
    # print("Scan code:", keyboard_event.scan_code)
    # print("Time:", keyboard_event.time)
    # check if the program is listening for a key
    if pressed == False:
      if keyboard_event.scan_code == 103 and operatingSystem == "linux" or keyboard_event.scan_code == 72 and operatingSystem == "windows": #up
        # go to the next selected file or server
        if selectedFile > 0:
          selectedFile -= 1

        if selectedServer > 0:
          selectedServer -= 1
        pressed = True

      if keyboard_event.scan_code == 108 and operatingSystem == "linux" or keyboard_event.scan_code == 80 and operatingSystem == "windows": #down
        # go to the previous file or server
        if selectedFile < len(filesList) - 1:
          selectedFile += 1

        if selectedServer < len(serverList) + 1:
          selectedServer += 1
        pressed = True

      if keyboard_event.scan_code == 105 and operatingSystem == "linux" or keyboard_event.scan_code == 75 and operatingSystem == "windows": #left
        # go to the previous command
        if selectedCommand > 0:
          selectedCommand -= 1

        if selectedLoginCommand > 0:
          selectedLoginCommand -= 1
        pressed = True

      if keyboard_event.scan_code == 106 and operatingSystem == "linux" or keyboard_event.scan_code == 77 and operatingSystem == "windows": #right
        # go to the next command
        if selectedCommand < len(commands) - 1:
          selectedCommand += 1

        if selectedLoginCommand < len(loginCommands) - 1:
          selectedLoginCommand += 1
        pressed = True

      # check for enter, used to select any option
      if keyboard_event.scan_code == 28:
        enter = True
        pressed = True


# USER MANAGEMENT FUNCTIONS

# function to login through /secret
def login(usernameL, passwordL):
  global serverMessage
  global username
  global password

  # try to encode the username and password in base64, if username and password exist, then
  if encodeBase64(usernameL, passwordL):
    # set the encoded string as an auth header
    headers = {
      'Authorization': 'Basic ' + encodeBase64(usernameL, passwordL)
    }

    # make an HTTP GET request to the webapi /secret
    r = requests.get(url + '/secret', headers = headers)

    # if the program returns 200 OK
    if r.status_code == 200:
      # set the current username as the one used for the request
      username = usernameL
      # set the current password as the one used for the request
      password = passwordL
      # wipe the server message
      serverMessage = ""
      return True

    # if the request returns an error 
    else:
      # print the error as the server message
      serverMessage = r.text
      return False

  return False

# function to login through /login
def loginCookie(usernameL, passwordL):
  global serverMessage
  global username
  global password

  # make an HTTP GET request to /login to login and get a cookie
  r = requests.post(url + '/login?username=' + usernameL + '&password=' + passwordL)

  # if the response is 200 OK
  if r.status_code == 200:
    # create or write a cookie.txt file with the cookie received from the response
    try:
      cookieFile = open("cookie.txt", "x")
      cookieFile.write(r.cookies["auth"])
      cookieFile.close()
    except IOError:
      cookieFile = open("cookie.txt", "w")
      cookieFile.write(r.cookies["auth"])
      cookieFile.close()

    # wipe the server message
    serverMessage = ""
    # set the current username to the one used in the request to login
    username = usernameL
    # set the current password to the one used in the request to login
    password = passwordL
    return True
    
  # if the response is anything else
  else:
    # show the error in the server message
    serverMessage = r.text
    return False

# function to automatically login to the server by using the cookie
def loginWithoutCredentials():
  global username
  
  # if there is a cookie to read
  if (readCookie()):
    # set the cookie in the header
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    # send an HTTP GET request to /secret to login through cookie
    r = requests.get(url + '/secret', headers = headers)
    
    # if the response is 200 OK
    if r.status_code == 200:
      # set the current username to the response message
      username = r.text
      return True 

    # if the response is anything else
    else:
      # set the error as server message to be displayed
      serverMessage = r.text;
      return False
    
# function to register a new user
def register(usernameL, passwordL):
  global serverMessage
  global username
  global password

  # if username and password exist and can be encoded in base64
  if encodeBase64(usernameL, passwordL):
    # set the auth header to the encoded string containing the username and password
    headers = {
      'Authorization': 'Basic ' + encodeBase64(usernameL, passwordL)
    }

    # make an HTTP POST request to /users
    r = requests.post(url + '/users', headers = headers)

    # if the response status is 200 OK
    if r.status_code == 200:
      # set the current username as the username used in the request
      username = usernameL
      # set the current password as the password used in the request
      password = passwordL
      # wipe the server message
      serverMessage = ""
      return True

    # if the response is anything else
    else:
      # show the error as the server message
      serverMessage = r.text
      return False
  
  return False

# function to delete an existing user
def deleteUser(usernameL, passwordL):
  global serverMessage

  # if the username and password exist and can be encoded base64
  if encodeBase64(usernameL, passwordL):
    # set the auth header with the username and password encoded in base64
    headers = {
      'Authorization': 'Basic ' + encodeBase64(usernameL, passwordL)
    }

    # make an HTTP DELETE request to /users
    r = requests.delete(url + '/users', headers = headers)

    # if the response is 200 OK
    if r.status_code == 200:
      # notify the success as the server message
      serverMessage = r.text
      return True

    # if the response is anything else
    else:
      # notify the error through the server message
      serverMessage = r.text
      return False
  
  return False


# PRINTING FUNCTIONS

# function to print all the files
def printFiles():
  global selectedFile
  global upToDate

  # check for the file list if something changed
  if not upToDate:
    checkFiles()
  
  print("\nFILES:")

  # iterate over the file list
  for i in range(0, len(filesList)):
    # print a red arrow and the file name is the item to print is the one selected
    if i == selectedFile:
      print(colored("> ", "red"), filesList[i])
    # print an arrow and the file name
    else:
      print("> " + filesList[i])

# function to get the list of all the files in a server
def checkFiles():
  global filesList
  global upToDate
  global serverMessage
  global serverCurrent
  global currentServerPassword

  # stores the previous file list to check if the input filelist from the minio server changed
  previousfilesList = filesList

  # make HTTP GET requests on /upload until it finds a new file list, different from the previous one
  while filesList == previousfilesList:
    r = requests.request("GET", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword)

    # if the request returns 200 OK
    if r.status_code == 200:
      # make a new fileIndexes array to store the index of the string containing the mod names
      fileIndexes = []
      # store all the indexes of the string that correspond to places with the character "
      for m in re.finditer('"', r.text):
        fileIndexes.append(m.start())

      # empty the files list
      filesList = []

      # cicle through the indexes containing the positions of the file names
      for i in range(0, len(fileIndexes)):
        # every 2 cycles
        if i % 2 == 1:
          # add the string between the last 2 characters ", aka the file name
          filesList.append(r.text[fileIndexes[i - 1] + 1 : fileIndexes[i]])

    # if the request returns a status code different from 200 OK
    else:
      # notify the error through the server message
      serverMessage = r.text

    # wait before trying again, in case the files list didn't change
    time.sleep(0.1)

  # notify that the file list is up to date
  upToDate = True

# function to print all the available commands
def printCommands():
  # iterate over the possible commands
  for i in range(len(commands)):
    # if we are printing the selected command, print it red
    if i == selectedCommand:
      color = "red"
    # otherwise print it white
    else:
      color = "white"

    # if we're printing the last command, just print the command
    if i == len(commands) - 1:
      print(colored(commands[i], color))
    # if we're printing any other command, leave a space between them
    else:
      print(colored(commands[i], color), "  ", end = '', flush = True)

# function to print all the available login commands
def printLoginCommands():
  # iterate over the possible commands to login
  for i in range(len(loginCommands)):
    # if we are printing the selected login command, print it in red
    if i == selectedLoginCommand:
      color = "red"
    # otherwise print it in white
    else:
      color = "white"

    # if we're printing the last login command, just print the command
    if i == len(loginCommands) - 1:
      print(colored(loginCommands[i], color))
    # if we're printing any other login command, leave a space between them
    else:
      print(colored(loginCommands[i], color), "  ", end = '', flush = True)

# function to print all the available servers
def printServers():
  global serverList
  global selectedServer
  global upToDateServer

  print("\nSERVERS: ")

  # if there was a change in the server list
  if not upToDateServer:
    # check the servers available
    checkServers()
    
  # print the New Server option, if it's the selected option, print it green
  if selectedServer == 0:
    print(colored("> ", "green"), colored("New Server\n", "green"))
  else:
    print("> New Server\n")

  # iterate over the servers list
  for i in range(0, len(serverList)):
    # if we're printing the selected server, color the arrow red
    if i + 1 == selectedServer:
      print(colored("> ", "red"), serverList[i])
    # otherwise print everything white
    else:
      print("> " + serverList[i])

  # print the Logout option, if it's the selected option, print it red
  if selectedServer == len(serverList) + 1:
    print(colored("\n>  Logout", "red"))
  else:
    print("\n> Logout")

# function to get the list of all the available servers
def checkServers():
  global serverList
  global upToDateServer

  # make an HTTP GET request to /servers
  r = requests.get(url + "/servers")

  # if the request returns 200 OK
  if r.status_code == 200:
    # wipe the serverList
    serverList = []
    # create a new serverIndexes array to store the position of the strings containing the server name
    serverIndexes = []

    # find instances of the character ", which defines the beginning and end of a server name string
    for m in re.finditer('"', r.text):
      # store their positions in the serverIndexes array
      serverIndexes.append(m.start())

    # iterate over the serverIndexes
    for i in range(0, len(serverIndexes)):
      # every 2 cycles
      if i % 2 == 1:
        # store the string in between the last 2 characters ", which is the server name
        serverList.append(r.text[serverIndexes[i - 1] + 1 : serverIndexes[i]])

  # notify that the server list is up to date
  upToDateServer = True


# SERVERS MANAGEMENT FUNCTIONS

# function to create a new server
def createServer(serverName, serverPassword):
  global serverMessage
  global username
  global password
  global upToDateServer
  global serverCurrent
  global currentServerPassword
  global serverOwner

  # try to read the cookies file
  if readCookie():
    # if a cookie file is found and a valid cookie inside is found
    # set it as a header
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    # make an HTTP POST request to /servers
    r = requests.post(url + "/servers" + "?serverName=" + serverName + "&serverPassword=" + serverPassword, headers = headers)

    # if the response is 200 OK
    if r.status_code == 200:
      # set the current server as the response text
      serverCurrent = r.text
      # set the current server password as the password set to the new server in the request
      currentServerPassword = serverPassword
      # set the user as server owner
      serverOwner = True
      # notify that the server list is not up to date anymore
      upToDateServer = False
      return True

    # if the response is anything else
    else:
      # set the error as server message
      serverMessage = r.text
      return False
  
  # try to encode username and password in base64
  if encodeBase64(username, password):
    # if the username and the password exist and can be encoded in base64
    # set the encoded string as an auth header
    headers = {
      'Authorization': 'Basic ' + encodeBase64(username, password)
    }

    # make an HTTP POST request to /servers
    r = requests.post(url + "/servers" + "?serverName=" + serverName + "&serverPassword=" + serverPassword, headers = headers)

    # if the response is 200 OK
    if r.status_code == 200:
      # set the server current as the response text
      serverCurrent = r.text
      # set the current server password as the one used to create the server
      currentServerPassword = serverPassword
      # set the user as the server owner
      serverOwner = True
      # notify that the server list is not up to date anymore
      upToDateServer = False
      return True

    # if the response is anything else 
    else:
      # set the error as server message
      serverMessage = r.text
      return False

  return False

# function to delete an existing server
def deleteServer():
  global serverCurrent
  global currentServerPassword
  global serverOwner
  global serverMessage
  global upToDateServer

  # try to read the cookie file
  if readCookie():
    # if the file exists and contains a valid cookie
    # set the cookie as a header
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    # make an HTTP DELETE request to /servers
    r = requests.delete(url + "/servers" + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)

    # if the response status is 200 OK
    if r.status_code == 200:
      # wipe the server current name
      serverCurrent = ""
      # wipe the server current password
      currentServerPassword = ""
      # set the user as non server owner
      serverOwner = False
      # notify that the server list is not up to date anymore
      upToDateServer = False
      return True

    # if the response is anything else
    else:
      # set the error as server message
      serverMessage = r.text
      return False

  # try to encode username and password in base64
  if encodeBase64(username, password):
    # if username and password exist and are valid
    # set the encoded string as auth header
    headers = {
      'Authorization': 'Basic ' + encodeBase64(username, password)
    }

    # make an HTTP DELETE request to /servers
    r = requests.delete(url + "/servers" + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)

    # if the response is 200 OK
    if r.status_code == 200:
      # wipe the server current name
      serverCurrent = ""
      # wipe the server current password
      currentServerPassword = ""
      # set the user as non server owner
      serverOwner = False
      # notify that the server list is not up to date
      upToDateServer = False
      return True

    # if the response is anything else
    else:
      # set the error as server message
      serverMessage = r.text
      return False

  return False

# function to login into a server
def loginServer(serverPassword):
  global serverList
  global serverMessage
  global serverCurrent
  global currentServerPassword
  global serverOwner
  global username

  # make an HTTP GET request to /servers
  r = requests.get(url + "/servers" + "?serverName=" + serverList[selectedServer - 1] + "&serverPassword=" + serverPassword)

  # if the response is 200 OK
  if r.status_code == 200:
    # store the response string containing server name and username
    info = r.text.split(",")
    # set the server current name as the server name in the response
    serverCurrent = info[0]
    # if the username in the response corresponds to the logged in user
    if info[1] == username:
      # set the user to server owner
      serverOwner = True
    # set the current server password to the password used to login
    currentServerPassword = serverPassword
    return True

  # if the response is anything else
  else:
    # set the error as server message
    serverMessage = r.text
    return False


# FILES MANAGEMENT FUNCTIONS

# function to upload a new file to a server
def uploadFile(path):
  global serverMessage
  global upToDate

  # split the string everytime "/" is encountered
  splitString = path.split("/")
  # set the filename as the last string after the last "/" character (which is the filename in the path)
  filename = splitString[len(splitString) - 1]

  payload = {}

  # set the request files field with the file name and opening the file through the paths in binary
  # sets the file nickname as "avatar" and the file MIME type as "application/octet-stream", to accomodate for every file type
  files = [
    ('avatar', (filename, open(path, 'rb'), 'application/octet-stream'))
  ]

  # try to read the cookie file
  if readCookie():
    # if the cookie file exists and contains a valid cookie
    # set the cookie as a header
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    # make an HTTP POST request to /upload
    r = requests.request("POST", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers, data = payload, files = files)

    # if the response is 200 OK
    if r.status_code == 200:
      # notify that the files list is not up to date
      upToDate = False
      return True

    # if the response is anything else
    else:
      # set the error as server message
      serverMessage = r.text
      return False

  # try to encode base64 the username and password
  if encodeBase64(username, password):
    # if the username and password exist and are valid
    # set the encoded string as an auth header
    headers = {
      'Authorization': 'Basic ' + encodeBase64(username, password)
    }

    # make an HTTP POST request to /upload
    r = requests.request("POST", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers, data = payload, files = files)

    # if the response is 200 OK
    if r.status_code == 200:
      # notify that the files list is not up to date
      upToDate = False
      return True

    # if the response is anything else
    else:
      # set the error as server message
      serverMessage = r.text
      return False

  return False

# function to download a file from a server
def downloadFile(fileName):
  global serverMessage

  # download path for the files to download
  downloadPath = "./download/"

  # try to make a folder in the path in case it doesn't exist already
  try:
    os.mkdir(downloadPath)
  except IOError:
    pass

  # try to read the cookie file
  if readCookie():
    # if the cookie file exists and contains a valid cookie
    # set the cookie as a header
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    # make an HTTP GET request to /download
    r = requests.request("GET", url + '/download' + "?fileName=" + fileName + "&serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)

    # if the response is 200 OK
    if r.status_code == 200:
      # try to open and write on the downloaded file
      # creating it if it doesn't already exist
      try:
        file = open(downloadPath + fileName, "xb")
        file.write(r.content)
      # or writing on it if it already exists
      except IOError:
        file = open(downloadPath + fileName, "wb")
        file.write(r.content)
      
      finally:
        return True
    
    # if the response is anything else
    else:
      # set the error as server message
      serverMessage = r.text
      return False
  
  # try to encode username and password in base64
  if encodeBase64(username, password):
    # if username and password exist and are valid
    # set the encoded string as auth header
    headers = {
      'Authorization': 'Basic ' + encodeBase64(username, password)
    }

    # make an HTTP GET request to /download
    r = requests.request("GET", url + '/download' + "?fileName=" + fileName + "&serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)
    
    # if the response is 200 OK
    if r.status_code == 200:
      # try to open and write on the downloaded file
      # creating if if it doesn't already exist
      try:
        file = open(downloadPath + fileName, "xb")
        file.write(r.content)
      # or writing on it if it already exists
      except IOError:
        file = open(downloadPath + fileName, "wb")
        file.write(r.content)
      
      finally:
        return True

    # if the response is anything else
    else:
      # set the error as server message
      serverMessage = r.text
      return False

  return False

# function to delete a file within a server
def deleteFile(fileName):
  global upToDate
  global serverMessage

  # try to read the cookie file
  if readCookie():
    # if the cookie file exists and contains a valid cookie
    # set the cookie as header
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    # make an HTTP DELETE request to /upload
    r = requests.request("DELETE", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword + "&fileName=" + fileName, headers = headers)

    # if the response is 200 OK
    if r.status_code == 200:
      # notify that the files list is not up to date
      upToDate = False
      return True

    # if the response is anything else
    else:
      # set the error as server message
      serverMessage = r.text
      return False

  # try to encode username and password in base64
  if encodeBase64(username, password):
    # if username and password exist and are valid
    # set the encoded string as auth header
    headers = {
      'Authorization': 'Basic ' + encodeBase64(username, password)
    }

    # make an HTTP DELETE request to /upload
    r = requests.request("DELETE", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword + "&fileName=" + fileName, headers = headers)

    # if the response is 200 OK
    if r.status_code == 200:
      # notify that the files list is not up to date
      upToDate = False
      return True

    # if the response is anything else
    else:
      # set the error as server message
      serverMessage = r.text
      return False

  return False


# MAIN FUNCTION

def main():
  # clear the screen
  clear()

  # access to global variables
  global enter
  global pressed
  global serverMessage
  global upToDateServer
  global upToDate
  global serverOwner
  global filesList
  global selectedFile

  # internal flags to determin the state of the program
  # to save if the program should be running or not
  running = True
  # to save if the user is logged in or not
  loggedIn = False
  # to save if the user is logged in a server or not
  serverLoggedIn = False

  # link the keyboard api to the function that handles inputs
  keyboard.on_press(keyboardEventHandler)

  # try to login through cookie
  if loginWithoutCredentials():
    loggedIn = True

  # MAIN LOOP
  while running:
    # print the server message (errors, info etc...)
    if (serverMessage != ""):
      print(colored(serverMessage + "\n", 'yellow'))

    # LOGIN
    if not loggedIn:
      # print the login commands (login, login with cookie, register, delete, close)
      printLoginCommands()
      
      # keyboard event polling
      while not pressed and not enter:
        pass
      pressed = False

      # login
      if selectedLoginCommand == 0 and enter == True:
        # clean the previous server message
        serverMessage = ""
        # flush the inputs buffer before getting user inputs
        flushInput()
        # get the username from the user
        usernameL = input("\nUsername: ")
        print()
        # get the password from the user without showing it
        passwordL = stdiomask.getpass(mask='*')
        # check if the login worked
        if login(usernameL, passwordL):
          loggedIn = True
        # set enter to false to listen for a new command
        enter = False

      # login with cookie
      elif selectedLoginCommand == 1 and enter == True:
        # clean the previous server message
        serverMessage = ""
        # flush the inputs buffer before getting user inputs
        flushInput()
        # get the username from the user
        usernameL = input("\nUsername: ")
        print()
        # get the password from the user without showing it
        passwordL = stdiomask.getpass(mask='*')
        # check if the login worked
        if loginCookie(usernameL, passwordL):
          loggedIn = True
        # set enter to false to listen for a new command
        enter = False

      # register
      elif selectedLoginCommand == 2 and enter == True:
        # clean the previous server message
        serverMessage = ""
        # flush the inputs buffer before getting user inputs
        flushInput()
        # get the username from the user
        usernameL = input("\nUsername: ")
        print()
        # get the password from the user without showing it
        passwordL = stdiomask.getpass(mask='*')
        # check if the registration worked
        if register(usernameL, passwordL):
          loggedIn = True
        # set enter to false to listen for a new command
        enter = False

      # delete 
      elif selectedLoginCommand == 3 and enter == True:
        # clean the previous server message
        serverMessage = ""
        # flush the inputs buffer before getting user inputs
        flushInput()
        # get the username from the user
        usernameL = input("\nUsername: ")
        print()
        # get the password from the user without showing it
        passwordL = stdiomask.getpass(mask='*')
        # delete the specified user if available
        deleteUser(usernameL, passwordL)
        enter = False

      # close
      elif selectedLoginCommand == 4 and enter == True:
        # set the variable running to False to terminate the program
        running = False
        # flush the input to prevent any inputs within the program to affect the father program
        flushInput()

      # clear the screen to set it ready for the next draw call
      clear()

    # SERVER LOGIN
    elif not serverLoggedIn:
      # print the current logged in user
      print("User: " + username)
      # print all the available servers and the server options on the screen
      printServers()

      # keyboard event polling
      while not pressed and not enter:
        pass
      pressed = False
      
      # if the user pressed enter (chose an option)
      if enter == True:
        # clean the server message
        serverMessage = ""

        # New server
        if selectedServer == 0:
          # clean the input buffer before a user input
          flushInput()
          # get the new server name from the user
          serverName = input("\nServer Name: ")
          # transform the server name into lower case (to match with the minio bucket, which only accepts lower case names)
          serverName = serverName.lower()
          print()
          # get the new server password from the user without showing it
          serverPassword = stdiomask.getpass(mask='*')
          # check if the new server was created correctly
          if createServer(serverName, serverPassword):
            # notify that the user is not logged in to the newly created server
            serverLoggedIn = True
            # notify to recheck the server list, now that a new server has been created
            upToDateServer = False
            # set the files list to "null" to notify that when entering the server, the file list should be redownloaded
            filesList = ["null"]
            # notify that the file list needs to be updated
            upToDate = False
            # sets the selected file to 0 to set it to the beginning, since there won't be any files to begin with
            selectedFile = 0
          # sets enter to false to listen for a new command
          enter = False

        # Logout
        elif selectedServer == len(serverList) + 1:
          # sets enter to false to listen for a new command
          enter = False
          # notify that the user is no longer logged in into any account
          loggedIn = False
          # notify that the user isn't the server owner anymore
          serverOwner = False

          # try to remove the cookie.txt file if it exists
          try:
            os.remove("cookie.txt")
          except IOError:
            print("No cookie to remove")

        # Login server
        else:
          # clean the input buffer before a user input
          flushInput()
          print()
          # get the server password from the user without showing it
          serverPassword = stdiomask.getpass(mask='*')
          # set enter to false to listen for new commands
          enter = False
          # check if the server login was succesful
          if loginServer(serverPassword):
            # notify that the user is logged into a server
            serverLoggedIn = True
            # set the fileslist to "null" to make it update
            filesList = ["null"]
            # notify that the files list needs to be updated
            upToDate = False
            # set the selected file to the first one
            selectedFile = 0

      # clear the screen
      clear()

    # FILE MANAGEMENT
    else:
      # if the user is the server owner
      if serverOwner:
        # print the user in blue color
        print("User:", colored(username, 'cyan'))
      # otherwise print the user normally
      else:
        print("User: " + username)

      # print the current server
      print("\nServer: " + serverCurrent)

      # print all the files within the current server
      printFiles()

      print()

      # print all the available commands inside a server
      printCommands()

      # keyboard event polling
      while not pressed and not enter:
        pass
      pressed = False

      # upload file
      if selectedCommand == 0 and enter == True:
        # wipe the server message
        serverMessage = ""
        # set enter to false to listen for a new input
        enter = False
        # try to open a file to upload
        try:
          # get the file path
          path = askopenfilename()
          # upload it to the server
          uploadFile(path)
        # if there's no file uploaded or any IOError
        except IOError:
          # notify the user of the error
          serverMessage = "No file selected"

      # download file
      elif selectedCommand == 1 and enter == True:
        # wipe the server message
        serverMessage = ""
        # set enter to false to listen for a new input
        enter = False
        # download the file specified
        downloadFile(filesList[selectedFile])

      # delete file
      elif selectedCommand == 2 and enter == True:
        # check if the file list isn't empty before deleting a file
        if len(filesList) == 0:
          # if the list of files is empty, notify the user that there's no file to delete
          serverMessage = "No file to delete!"
          # set enter to false to listen for a new input
          enter = False
        else:
          # wipe the server message
          serverMessage = ""
          # clean the input buffer
          flushInput()
          # ask the user if they are sure about the choice
          choice = input("Are you sure? [Yes/No]: ")
          # set enter to false to listen for a new input
          enter = False
          # if the user choice was positive
          if choice == "Yes" or choice == "yes" or choice == "ye" or choice == "y":
            # delete the selected file
            deleteFile(filesList[selectedFile])

      # change server
      elif selectedCommand == 3 and enter == True:
        # wipe the server message
        serverMessage = ""
        # set enter to false to listen for a new input
        enter = False
        # logout from the server
        serverLoggedIn = False
        # set the server owner to false, since we're not inside any server anymore
        serverOwner = False
        
      # delete server
      elif selectedCommand == 4 and enter == True:
        # wipe the server message
        serverMessage = ""
        # clean the input buffer
        flushInput()
        # ask the user if they are sure about the choice
        choice = input("Are you sure? [Yes/No]: ")
        # set enter to false to listen for a new input
        enter = False
        # if the user choice was positive
        if choice == "Yes" or choice == "yes" or choice == "ye" or choice == "y":
          # delete the server
          if deleteServer():
            # logout of the server
            serverLoggedIn = False
            # set the server owner to false since there's no server anymore
            serverOwner = False
            # notify that the server list needs to be updated
            upToDateServer = False

      # logout
      elif selectedCommand == 5 and enter == True:
        # wipe the server message
        serverMessage = ""
        # set enter to false to listen for new inputs
        enter = False
        # logout of the account
        loggedIn = False
        # logout of the server
        serverLoggedIn = False
        # set the server owner to false, since we're not logged in to a server anymore
        serverOwner = False
        # try to remove the cookie file in case it's there
        try:
          os.remove("cookie.txt")
        except IOError:
          print("No cookie to remove")
        
      # close
      elif selectedCommand == 6 and enter == True:
        # set enter to false to listen for new inputs
        enter = False
        # stops the program from running
        running = False
        # clear the inputs before closing
        flushInput()
        
      # clean the screen
      clear()


if __name__ == "__main__":
  main()