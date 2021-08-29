import requests
import base64
import re
import os
import keyboard
import msvcrt
import sys
import stdiomask
import time
from termcolor import colored
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

url = "https://projectpdgt.herokuapp.com"
# url = "http://localhost:2000"

serverCurrent = ""

modList = []

serverList = []

selectedServer = 0

upToDate = True

upToDateServer = False

Tk().withdraw()

selectedMod = 0

selectedCommand = 0

pressed = False

selectedLoginCommand = 0

enter = False

serverMessage = ""

loginCommands = ["Login", "Login with Cookie", "Register", "Delete", "Close"]

commands = ["Upload Mod", "Download Mod", "Change Server", "Logout", "Close"]

username = ""
password = ""

currentServerPassword = ""

serverOwner = False


def login(usernameL, passwordL):
  global username
  global serverMessage
  global username
  global password

  credentials = usernameL + ":" + passwordL
  credentials_bytes = credentials.encode('ascii')
  base64_bytes = base64.b64encode(credentials_bytes)
  base64_message = base64_bytes.decode('ascii')

  headers = {
    'Authorization': 'Basic ' + base64_message
  }

  r = requests.get(url + '/secret', headers = headers)

  if r.status_code == 200:
    username = r.text
    username = usernameL
    password = passwordL
    serverMessage = ""
    return True
    
  else:
    serverMessage = r.text
    return False

def loginCookie(usernameL, passwordL):
  global username
  global serverMessage
  global username
  global password

  r = requests.post(url + '/login?username=' + usernameL + '&password=' + passwordL)

  if r.status_code == 200:
    username = r.text
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

def loginWithoutCredentials():
  global username
  try:
    cookieFile = open("cookie.txt", "r")
    headers = {
      'Cookie': 'auth=' + cookieFile.read()
    }
    cookieFile.close()
    x = requests.get(url + '/secret', headers = headers)
    
    if int(x.status_code) == 200:
      username = x.text
      return True 
      
    else:
      return False

  except IOError:
    return False

def register(usernameL, passwordL):
  global serverMessage
  global username
  global username
  global password

  credentials = usernameL + ":" + passwordL
  credentials_bytes = credentials.encode('ascii')
  base64_bytes = base64.b64encode(credentials_bytes)
  base64_message = base64_bytes.decode('ascii')

  headers = {
    'Authorization': 'Basic ' + base64_message
  }

  r = requests.post(url + '/users', headers = headers)

  if r.status_code == 200:
    username = r.text
    username = usernameL
    password = passwordL
    serverMessage = ""
    return True
  else:
    serverMessage = r.text
    return False

def deleteUser(username, password):
  global serverMessage

  credentials = username + ":" + password
  credentials_bytes = credentials.encode('ascii')
  base64_bytes = base64.b64encode(credentials_bytes)
  base64_message = base64_bytes.decode('ascii')

  headers = {
    'Authorization': 'Basic ' + base64_message
  }

  r = requests.delete(url + '/users', headers = headers)

  if r.status_code == 200:
    serverMessage = r.text
    return True
  else:
    serverMessage = r.text
    return False


def printMods():
  global selectedMod
  global upToDate

  if not upToDate:
    checkMods()
  
  print("\nMODS:")

  for i in range(0, len(modList)):
    if i == selectedMod:
      print(colored("> ", "red"), modList[i])
    else:
      print("> " + modList[i])

def checkMods():
  global modList
  global upToDate
  global serverMessage
  global serverCurrent
  global currentServerPassword

  previousModList = modList

  while modList == previousModList:
    r = requests.request("GET", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword)

    if r.status_code == 200:
      modIndexes = []
      for m in re.finditer('"', r.text):
        modIndexes.append(m.start())

      modList = []

      for i in range(0, len(modIndexes)):
        if i % 2 == 1:
          modList.append(r.text[modIndexes[i - 1] + 1 : modIndexes[i]])
          # print("> " + r.text[modIndexes[i - 1] + 1 : modIndexes[i]])

      # print(modList)
      
      # if previousModList == modList:
      #   upToDate = False
      # else:
      #   upToDate = True

      # print(modList)
      # print(previousModList)

    else:
      serverMessage = r.text

    time.sleep(0.1)

  upToDate = True

def getMods():
  global modList
  global upToDate
  global serverMessage
  global serverCurrent
  global currentServerPassword

  r = requests.request("GET", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword)

  if r.status_code == 200:
    modIndexes = []
    for m in re.finditer('"', r.text):
      modIndexes.append(m.start())

    modList = []

    for i in range(0, len(modIndexes)):
      if i % 2 == 1:
        modList.append(r.text[modIndexes[i - 1] + 1 : modIndexes[i]])
        # print("> " + r.text[modIndexes[i - 1] + 1 : modIndexes[i]])

    # print(modList)
    
    # if previousModList == modList:
    #   upToDate = False
    # else:
    #   upToDate = True

    # print(modList)
    # print(previousModList)

  else:
    serverMessage = r.text


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

def createServer(serverName, serverPassword):
  global serverMessage
  global username
  global password
  global upToDateServer
  global serverCurrent
  global currentServerPassword
  global serverOwner

  try:
    cookieFile = open("cookie.txt", "r")
    headers = {
      'Cookie': 'auth=' + cookieFile.read()
    }
    cookieFile.close()
    r = requests.post(url + "/servers" + "?serverName=" + serverName + "&serverPassword=" + serverPassword, headers = headers)

    if r.status_code == 200:
      serverCurrent = r.text
      currentServerPassword = serverPassword
      serverOwner = True
      return True
    else:
      serverMessage = r.text
      return False

  except IOError:
    credentials = username + ":" + password
    credentials_bytes = credentials.encode('ascii')
    base64_bytes = base64.b64encode(credentials_bytes)
    base64_message = base64_bytes.decode('ascii')

    headers = {
      'Authorization': 'Basic ' + base64_message
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


def uploadMod(path):
  global serverMessage
  global serverCurrent
  global currentServerPassword
  global upToDate

  splitString = path.split("/")
  filename = splitString[len(splitString) - 1]

  payload = {}

  files=[
    ('avatar',(filename, open(path,'rb'),'application/java-archive'))
  ]

  try:
    cookieFile = open("cookie.txt", "r")
    headers = {
      'Cookie': 'auth=' + cookieFile.read()
    }
    cookieFile.close()
    r = requests.request("POST", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers, data = payload, files = files)

    if r.status_code == 200:
      upToDate = False
      return True

    elif r.status_code == 403:
      serverMessage = r.text
      return False
      
    else:
      if username != "" and password != "":
        credentials = username + ":" + password
        credentials_bytes = credentials.encode('ascii')
        base64_bytes = base64.b64encode(credentials_bytes)
        base64_message = base64_bytes.decode('ascii')

        headers = {
          'Authorization': 'Basic ' + base64_message
        }

        r = requests.request("POST", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers, data = payload, files = files)

        if r.status_code == 200:
          upToDate = False
          return True
        else:
          serverMessage = r.text
          return False

      else:
        return False
      

  except IOError:
    if username != "" and password != "":
      credentials = username + ":" + password
      credentials_bytes = credentials.encode('ascii')
      base64_bytes = base64.b64encode(credentials_bytes)
      base64_message = base64_bytes.decode('ascii')

      headers = {
        'Authorization': 'Basic ' + base64_message
      }

      r = requests.request("POST", url + '/upload' + "?serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers, data = payload, files = files)

      if r.status_code == 200:
        upToDate = False
        return True
      else:
        serverMessage = r.text
        return False
    
    else:
      return False

def downloadMod(modName):
  global serverMessage
  global serverCurrent
  global currentServerPassword

  downloadPath = "./download/"

  try:
    cookieFile = open("cookie.txt", "r")
    headers = {
      'Cookie': 'auth=' + cookieFile.read()
    }
    cookieFile.close()
    r = requests.request("GET", url + '/download' + "?mod=" + modName + "&serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)

    if r.status_code == 200:
      try:
        file = open(downloadPath + modName, "xb")
        file.write(r.content)

      except IOError:
        file = open(downloadPath + modName, "wb")
        file.write(r.content)
      
      finally:
        return True
    
    elif r.status_code == 404:
      serverMessage = r.text
      return False

    else:
      if username != "" and password != "":
        credentials = username + ":" + password
        credentials_bytes = credentials.encode('ascii')
        base64_bytes = base64.b64encode(credentials_bytes)
        base64_message = base64_bytes.decode('ascii')

        headers = {
          'Authorization': 'Basic ' + base64_message
        }

        r = requests.request("GET", url + '/download' + "?mod=" + modName + "&serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)

        if r.status_code == 200:
          try:
            file = open(downloadPath + modName, "xb")
            file.write(r.content)

          except IOError:
            file = open(downloadPath + modName, "wb")
            file.write(r.content)
          
          finally:
            return True

        else:
          serverMessage = r.text
          return False

      else:
        return False

  except IOError:
      if username != "" and password != "":
        credentials = username + ":" + password
        credentials_bytes = credentials.encode('ascii')
        base64_bytes = base64.b64encode(credentials_bytes)
        base64_message = base64_bytes.decode('ascii')

        headers = {
          'Authorization': 'Basic ' + base64_message
        }

        r = requests.request("GET", url + '/download' + "?mod=" + modName + "&serverName=" + serverCurrent + "&serverPassword=" + currentServerPassword, headers = headers)

        if r.status_code == 200:
          try:
            file = open(downloadPath + modName, "xb")
            file.write(r.content)

          except IOError:
            file = open(downloadPath + modName, "wb")
            file.write(r.content)
          
          finally:
            return True
            
        else:
          serverMessage = r.text
          return False

      else:
        return False



  # r = requests.request("GET", url + '/download' + "?mod=" + modName)
  # # print(r.status_code)

  # # downloadPath = "C:/Users/Joshua/AppData/Roaming/.minecraft/mods/"
  

  # try:
  #   file = open(downloadPath + modName, "xb")
  #   file.write(r.content)

  # except IOError:
  #   file = open(downloadPath + modName, "wb")
  #   file.write(r.content)

def my_keyboard_hook(keyboard_event):
    global selectedMod
    global pressed
    global selectedCommand
    global enter
    global selectedLoginCommand
    global loginCommands
    global selectedServer
    # print("Name:", keyboard_event.name)
    # print("Scan code:", keyboard_event.scan_code)
    # print("Time:", keyboard_event.time)
    if pressed == False:
      if keyboard_event.scan_code == 72: #up
        if selectedMod > 0:
          selectedMod -= 1

        if selectedServer > 0:
          selectedServer -= 1
        pressed = True

      if keyboard_event.scan_code == 80: #down
        if selectedMod < len(modList) - 1:
          selectedMod += 1

        if selectedServer < len(serverList) + 1:
          selectedServer += 1
        pressed = True

      if keyboard_event.scan_code == 75: #left
        if selectedCommand > 0:
          selectedCommand -= 1

        if selectedLoginCommand > 0:
          selectedLoginCommand -= 1
        pressed = True

      if keyboard_event.scan_code == 77: #right
        if selectedCommand < len(commands) - 1:
          selectedCommand += 1

        if selectedLoginCommand < len(loginCommands) - 1:
          selectedLoginCommand += 1
        pressed = True

      if keyboard_event.scan_code == 28:
        enter = True
        pressed = True


def main():
  os.system('cls')
  global enter
  global pressed
  global serverMessage
  global username
  global password
  global upToDateServer
  global serverCurrent
  global upToDate
  global serverOwner
  global modList
  global selectedMod

  running = True
  loggedIn = False
  serverLoggedIn = False
  keyboard.on_press(my_keyboard_hook)

  if loginWithoutCredentials():
    loggedIn = True

  while running:
    if (serverMessage != ""):
      print(serverMessage + "\n")

    # LOGIN

    if not loggedIn:

      printLoginCommands()

      serverMessage = ""
      
      while not pressed and not enter:
        pass
      pressed = False

      if selectedLoginCommand == 0 and enter == True:
        while msvcrt.kbhit():
          msvcrt.getch()
        sys.stdin.flush()
        usernameL = input("\nUsername: ")
        print()
        passwordL = stdiomask.getpass(mask='*')
        if login(usernameL, passwordL):
          loggedIn = True
        enter = False

      elif selectedLoginCommand == 1 and enter == True:
        while msvcrt.kbhit():
          msvcrt.getch()
        sys.stdin.flush()
        usernameL = input("\nUsername: ")
        print()
        passwordL = stdiomask.getpass(mask='*')
        if loginCookie(usernameL, passwordL):
          loggedIn = True
        enter = False

      elif selectedLoginCommand == 2 and enter == True:
        while msvcrt.kbhit():
          msvcrt.getch()
        sys.stdin.flush()
        usernameL = input("\nUsername: ")
        print()
        passwordL = stdiomask.getpass(mask='*')
        if register(usernameL, passwordL):
          loggedIn = True
        enter = False
        
      elif selectedLoginCommand == 3 and enter == True:
        while msvcrt.kbhit():
          msvcrt.getch()
        sys.stdin.flush()
        usernameL = input("\nUsername: ")
        print()
        passwordL = stdiomask.getpass(mask='*')
        deleteUser(usernameL, passwordL)
        enter = False

      elif selectedLoginCommand == 4 and enter == True:
        running = False

      os.system('cls')

    # SERVER LOGIN

    elif not serverLoggedIn:
      print("User: " + username)

      printServers()

      serverMessage = ""

      while not pressed and not enter:
        pass
      pressed = False
      
      if enter == True:
        if selectedServer == 0:
          while msvcrt.kbhit():
            msvcrt.getch()
          sys.stdin.flush()
          serverName = input("\nServer Name: ")
          serverName = serverName.lower()
          print()
          serverPassword = stdiomask.getpass(mask='*')
          if createServer(serverName, serverPassword):
            enter = False
            serverLoggedIn = True
            upToDateServer = False
            modList = ["null"]
            upToDate = False
            selectedMod = 0

        elif selectedServer == len(serverList) + 1:
          enter = False
          loggedIn = False
          serverOwner = False

          try:
            os.remove("cookie.txt")
          except IOError:
            print("No cookie to remove")


        else:
          while msvcrt.kbhit():
            msvcrt.getch()
          sys.stdin.flush()
          print()
          serverPassword = stdiomask.getpass(mask='*')
          if loginServer(serverPassword):
            enter = False
            serverLoggedIn = True
            modList = ["null"]
            upToDate = False
            selectedMod = 0
            # getMods()

      os.system('cls')

    # MOD MANAGEMENT

    else:
      if serverOwner:
        print("User:", colored(username, 'cyan'))
      else:
        print("User: " + username)

      print("\nServer: " + serverCurrent)

      printMods()

      print()

      printCommands()

      pressed = False
      while not pressed and not enter:
        pass
      pressed = False


      if selectedCommand == 0 and enter == True:
        serverMessage = ""
        enter = False
        try:
          path = askopenfilename()
          uploadMod(path)
        except IOError:
          print("File error")

      elif selectedCommand == 1 and enter == True:
        serverMessage = ""
        enter = False
        downloadMod(modList[selectedMod])

      elif selectedCommand == 2 and enter == True:
        serverMessage = ""
        enter = False
        serverLoggedIn = False
        serverOwner = False
        
      elif selectedCommand == 3 and enter == True:
        serverMessage = ""
        enter = False
        loggedIn = False
        serverLoggedIn = False
        serverOwner = False
        try:
          os.remove("cookie.txt")
        except IOError:
          print("No cookie to remove")
        
      elif selectedCommand == 4 and enter == True:
        enter = False
        running = False
        
      os.system('cls')


main()