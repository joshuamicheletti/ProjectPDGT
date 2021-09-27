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

  try:
    os.mkdir(downloadPath)
  except IOError:
    pass

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