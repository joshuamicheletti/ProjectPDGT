import requests
import base64
import re
import os
import keyboard
import sys
import stdiomask
import time
from termcolor import colored
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

try:
  import sys, termios
  operatingSystem = "linux"
except ImportError:
  import msvcrt
  operatingSystem = "windows"

Tk().withdraw()

url = "https://projectpdgt.herokuapp.com"
# url = "http://localhost:2000"

serverCurrent = ""

filesList = []

serverList = []

selectedServer = 0

upToDate = True

upToDateServer = False

selectedFile = 0

selectedCommand = 0

pressed = False

selectedLoginCommand = 0

enter = False

serverMessage = ""

loginCommands = ["Login", "Login with Cookie", "Register", "Delete", "Close"]

commands = ["Upload File", "Download File", "Delete File", "Change Server", "Delete Server", "Logout", "Close"]

username = ""
password = ""

currentServerPassword = ""

serverOwner = False

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
    if pressed == False:
      if keyboard_event.scan_code == 103 and operatingSystem == "linux" or keyboard_event.scan_code == 72 and operatingSystem == "windows": #up
        if selectedFile > 0:
          selectedFile -= 1

        if selectedServer > 0:
          selectedServer -= 1
        pressed = True

      if keyboard_event.scan_code == 108 and operatingSystem == "linux" or keyboard_event.scan_code == 80 and operatingSystem == "windows": #down
        if selectedFile < len(filesList) - 1:
          selectedFile += 1

        if selectedServer < len(serverList) + 1:
          selectedServer += 1
        pressed = True

      if keyboard_event.scan_code == 105 and operatingSystem == "linux" or keyboard_event.scan_code == 75 and operatingSystem == "windows": #left
        if selectedCommand > 0:
          selectedCommand -= 1

        if selectedLoginCommand > 0:
          selectedLoginCommand -= 1
        pressed = True

      if keyboard_event.scan_code == 106 and operatingSystem == "linux" or keyboard_event.scan_code == 77 and operatingSystem == "windows": #right
        if selectedCommand < len(commands) - 1:
          selectedCommand += 1

        if selectedLoginCommand < len(loginCommands) - 1:
          selectedLoginCommand += 1
        pressed = True

      if keyboard_event.scan_code == 28:
        enter = True
        pressed = True


# function to login through /secret
def login(usernameL, passwordL):
  global serverMessage
  global username
  global password

  if encodeBase64(usernameL, passwordL):

    headers = {
      'Authorization': 'Basic ' + encodeBase64(usernameL, passwordL)
    }

    r = requests.get(url + '/secret', headers = headers)

    if r.status_code == 200:
      username = usernameL
      password = passwordL
      serverMessage = ""
      return True
      
    else:
      serverMessage = r.text
      return False

  return False

# function to login through /login
def loginCookie(usernameL, passwordL):
  global serverMessage
  global username
  global password

  r = requests.post(url + '/login?username=' + usernameL + '&password=' + passwordL)

  if r.status_code == 200:
    try:
      cookieFile = open("cookie.txt", "x")
      cookieFile.write(r.cookies["auth"])
      cookieFile.close()
    except IOError:
      cookieFile = open("cookie.txt", "w")
      cookieFile.write(r.cookies["auth"])
      cookieFile.close()

    serverMessage = ""
    username = usernameL
    password = passwordL
    return True
    
  else:
    serverMessage = r.text
    return False

# function to automatically login to the server by using the cookie
def loginWithoutCredentials():
  global username
  
  if (readCookie()):
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    r = requests.get(url + '/secret', headers = headers)
    
    if r.status_code == 200:
      username = r.text
      return True 
      
  return False

# function to register a new user
def register(usernameL, passwordL):
  global serverMessage
  global username
  global password

  if encodeBase64(usernameL, passwordL):
    headers = {
      'Authorization': 'Basic ' + encodeBase64(usernameL, passwordL)
    }

    r = requests.post(url + '/users', headers = headers)

    if r.status_code == 200:
      username = usernameL
      password = passwordL
      serverMessage = ""
      return True
    else:
      serverMessage = r.text
      return False
  
  return False

# function to delete an existing user
def deleteUser(usernameL, passwordL):
  global serverMessage

  if encodeBase64(usernameL, passwordL):
    headers = {
      'Authorization': 'Basic ' + encodeBase64(usernameL, passwordL)
    }

    r = requests.delete(url + '/users', headers = headers)

    if r.status_code == 200:
      serverMessage = r.text
      return True
    else:
      serverMessage = r.text
      return False
  
  return False


# function to print all the files
def printFiles():
  global selectedFile
  global upToDate

  if not upToDate:
    checkFiles()
  
  print("\nFILES:")

  for i in range(0, len(filesList)):
    if i == selectedFile:
      print(colored("> ", "red"), filesList[i])
    else:
      print("> " + filesList[i])

# function to get the list of all the files in a server
def checkFiles():
  global filesList
  global upToDate
  global serverMessage
  global serverCurrent
  global currentServerPassword

  previousfilesList = filesList

  while filesList == previousfilesList:
    r = requests.request("GET", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword)

    if r.status_code == 200:
      fileIndexes = []
      for m in re.finditer('"', r.text):
        fileIndexes.append(m.start())

      filesList = []

      for i in range(0, len(fileIndexes)):
        if i % 2 == 1:
          filesList.append(r.text[fileIndexes[i - 1] + 1 : fileIndexes[i]])

    else:
      serverMessage = r.text

    time.sleep(0.1)

  upToDate = True

# function to print all the available commands
def printCommands():
  for i in range(len(commands)):
    if i == selectedCommand:
      color = "red"
    else:
      color = "white"

    if i == len(commands) - 1:
      print(colored(commands[i], color))
    else:
      print(colored(commands[i], color), "  ", end = '', flush = True)

# function to print all the available login commands
def printLoginCommands():
  for i in range(len(loginCommands)):
    if i == selectedLoginCommand:
      color = "red"
    else:
      color = "white"

    if i == len(loginCommands) - 1:
      print(colored(loginCommands[i], color))
    else:
      print(colored(loginCommands[i], color), "  ", end = '', flush = True)


# function to print all the available servers
def printServers():
  global serverList
  global selectedServer
  global upToDateServer
  print("\nSERVERS: ")

  if not upToDateServer:
    checkServers()

  if selectedServer == 0:
    print(colored("> ", "green"), colored("New Server\n", "green"))
  else:
    print("> New Server\n")

  for i in range(0, len(serverList)):
    if i + 1 == selectedServer:
      print(colored("> ", "red"), serverList[i])
    else:
      print("> " + serverList[i])

  if selectedServer == len(serverList) + 1:
    print(colored("\n>  Logout", "red"))
  else:
    print("\n> Logout")

# function to get the list of all the available servers
def checkServers():
  global serverList
  global upToDateServer

  r = requests.get(url + "/servers")

  if r.status_code == 200:
    serverList = []
    serverIndexes = []
    for m in re.finditer('"', r.text):
      serverIndexes.append(m.start())

    for i in range(0, len(serverIndexes)):
      if i % 2 == 1:
        serverList.append(r.text[serverIndexes[i - 1] + 1 : serverIndexes[i]])

  upToDateServer = True

# function to create a new server
def createServer(serverName, serverPassword):
  global serverMessage
  global username
  global password
  global upToDateServer
  global serverCurrent
  global currentServerPassword
  global serverOwner

  if readCookie():
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    r = requests.post(url + "/servers" + "?serverName=" + serverName + "&serverPassword=" + serverPassword, headers = headers)

    if r.status_code == 200:
      serverCurrent = r.text
      currentServerPassword = serverPassword
      serverOwner = True
      return True
    else:
      serverMessage = r.text
      return False
  
  if encodeBase64(username, password):
    headers = {
      'Authorization': 'Basic ' + encodeBase64(username, password)
    }

    r = requests.post(url + "/servers" + "?serverName=" + serverName + "&serverPassword=" + serverPassword, headers = headers)

    if r.status_code == 200:
      serverCurrent = r.text
      currentServerPassword = serverPassword
      serverOwner = True
      upToDateServer = False
      return True
    else:
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

  if readCookie():
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    r = requests.delete(url + "/servers" + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)

    if r.status_code == 200:
      serverCurrent = ""
      currentServerPassword = ""
      serverOwner = False
      upToDateServer = False
      return True
    else:
      serverMessage = r.text
      return False

  if encodeBase64(username, password):
    headers = {
      'Authorization': 'Basic ' + encodeBase64(username, password)
    }

    r = requests.delete(url + "/servers" + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)

    if r.status_code == 200:
      serverCurrent = ""
      currentServerPassword = ""
      serverOwner = False
      upToDateServer = False
      return True
    else:
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

  r = requests.get(url + "/servers" + "?serverName=" + serverList[selectedServer - 1] + "&serverPassword=" + serverPassword)

  if r.status_code == 200:
    info = r.text.split(",")
    serverCurrent = info[0]
    if info[1] == username:
      serverOwner = True
    currentServerPassword = serverPassword
    return True
  else:
    serverMessage = r.text
    return False


# function to upload a new file to a server
def uploadFile(path):
  global serverMessage
  global upToDate

  splitString = path.split("/")
  filename = splitString[len(splitString) - 1]

  payload = {}

  # DOUBLE CHECK THIS PIECE OF CODE
  files = [
    ('avatar',(filename, open(path,'rb'),'application/octet-stream'))
  ]

  if readCookie():
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    r = requests.request("POST", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers, data = payload, files = files)

    if r.status_code == 200:
      upToDate = False
      return True

    else:
      serverMessage = r.text
      return False

  if encodeBase64(username, password):
    headers = {
      'Authorization': 'Basic ' + encodeBase64(username, password)
    }

    r = requests.request("POST", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers, data = payload, files = files)

    if r.status_code == 200:
      upToDate = False
      return True
    else:
      serverMessage = r.text
      return False

  return False

# function to download a file from a server
def downloadFile(fileName):
  global serverMessage

  downloadPath = "./download/"

  if readCookie():
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    r = requests.request("GET", url + '/download' + "?fileName=" + fileName + "&serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)

    if r.status_code == 200:
      try:
        file = open(downloadPath + fileName, "xb")
        file.write(r.content)

      except IOError:
        file = open(downloadPath + fileName, "wb")
        file.write(r.content)
      
      finally:
        return True
    
    else:
      serverMessage = r.text
      return False
  
  if encodeBase64(username, password):
    headers = {
      'Authorization': 'Basic ' + encodeBase64(username, password)
    }

    r = requests.request("GET", url + '/download' + "?fileName=" + fileName + "&serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)
    
    if r.status_code == 200:
      try:
        file = open(downloadPath + fileName, "xb")
        file.write(r.content)

      except IOError:
        file = open(downloadPath + fileName, "wb")
        file.write(r.content)
      
      finally:
        return True

    else:
      serverMessage = r.text
      return False

  return False

# function to delete a file within a server
def deleteFile(fileName):
  global upToDate
  global serverMessage

  if readCookie():
    headers = {
      'Cookie': 'auth=' + readCookie()
    }

    r = requests.request("DELETE", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword + "&fileName=" + fileName, headers = headers)

    if r.status_code == 200:
      upToDate = False
      return True

    else:
      serverMessage = r.text
      return False

  if encodeBase64(username, password):
    headers = {
      'Authorization': 'Basic ' + encodeBase64(username, password)
    }

    r = requests.request("DELETE", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword + "&fileName=" + fileName, headers = headers)

    if r.status_code == 200:
      upToDate = False
      return True
    else:
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
        serverMessage = ""
        flushInput()
        usernameL = input("\nUsername: ")
        print()
        passwordL = stdiomask.getpass(mask='*')
        if loginCookie(usernameL, passwordL):
          loggedIn = True
        enter = False

      # register
      elif selectedLoginCommand == 2 and enter == True:
        serverMessage = ""
        flushInput()
        usernameL = input("\nUsername: ")
        print()
        passwordL = stdiomask.getpass(mask='*')
        if register(usernameL, passwordL):
          loggedIn = True
        enter = False

      # delete 
      elif selectedLoginCommand == 3 and enter == True:
        serverMessage = ""
        flushInput()
        usernameL = input("\nUsername: ")
        print()
        passwordL = stdiomask.getpass(mask='*')
        deleteUser(usernameL, passwordL)
        enter = False

      # close
      elif selectedLoginCommand == 4 and enter == True:
        running = False
        flushInput()

      clear()

    # SERVER LOGIN
    elif not serverLoggedIn:
      print("User: " + username)

      printServers()

      while not pressed and not enter:
        pass
      pressed = False
      
      if enter == True:
        serverMessage = ""

        # New server
        if selectedServer == 0:
          flushInput()
          serverName = input("\nServer Name: ")
          serverName = serverName.lower()
          print()
          serverPassword = stdiomask.getpass(mask='*')
          if createServer(serverName, serverPassword):
            serverLoggedIn = True
            upToDateServer = False
            filesList = ["null"]
            upToDate = False
            selectedFile = 0
          enter = False

        # Logout
        elif selectedServer == len(serverList) + 1:
          enter = False
          loggedIn = False
          serverOwner = False

          try:
            os.remove("cookie.txt")
          except IOError:
            print("No cookie to remove")

        # Login server
        else:
          flushInput()
          print()
          serverPassword = stdiomask.getpass(mask='*')
          enter = False
          if loginServer(serverPassword):
            serverLoggedIn = True
            filesList = ["null"]
            upToDate = False
            selectedFile = 0

      clear()

    # FILE MANAGEMENT
    else:
      if serverOwner:
        print("User:", colored(username, 'cyan'))
      else:
        print("User: " + username)

      print("\nServer: " + serverCurrent)

      printFiles()

      print()

      printCommands()

      pressed = False
      while not pressed and not enter:
        pass
      pressed = False

      # upload file
      if selectedCommand == 0 and enter == True:
        serverMessage = ""
        enter = False
        try:
          path = askopenfilename()
          uploadFile(path)
        except IOError:
          print("File error")

      # download file
      elif selectedCommand == 1 and enter == True:
        serverMessage = ""
        enter = False
        downloadFile(filesList[selectedFile])

      # delete file
      elif selectedCommand == 2 and enter == True:
        if len(filesList) == 0:
          serverMessage = "No file to delete!"
          enter = False
        else:
          serverMessage = ""
          flushInput()
          choice = input("Are you sure? [Yes/No]: ")
          enter = False
          if choice == "Yes" or choice == "yes" or choice == "ye" or choice == "y":
            deleteFile(filesList[selectedFile])

      # change server
      elif selectedCommand == 3 and enter == True:
        serverMessage = ""
        enter = False
        serverLoggedIn = False
        serverOwner = False
        
      # delete server
      elif selectedCommand == 4 and enter == True:
        serverMessage = ""
        flushInput()
        choice = input("Are you sure? [Yes/No]: ")
        enter = False
        if choice == "Yes" or choice == "yes" or choice == "ye" or choice == "y":
          if deleteServer():
            serverLoggedIn = False
            serverOwner = False
            upToDateServer = False

      # logout
      elif selectedCommand == 5 and enter == True:
        serverMessage = ""
        enter = False
        loggedIn = False
        serverLoggedIn = False
        serverOwner = False
        try:
          os.remove("cookie.txt")
        except IOError:
          print("No cookie to remove")
        
      # close
      elif selectedCommand == 6 and enter == True:
        enter = False
        running = False
        flushInput()
        
      clear()


if __name__ == "__main__":
  main()