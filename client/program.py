import requests
import base64
import re
import os
import keyboard
import msvcrt
import sys
from termcolor import colored
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

url = "https://projectpdgt.herokuapp.com"
# url = "http://localhost:2000"

user = ""

modList = []

upToDate = False

Tk().withdraw()

selectedMod = 0

selectedCommand = 0

pressed = False

selectedLoginCommand = 0

enter = False

serverMessage = ""

loginCommands = ["Login", "Login with Cookie", "Register", "Delete", "Close"]

commands = ["Upload Mod", "Download Mod", "LogOut", "Close"]


def login(username, password):
  global user
  global serverMessage

  credentials = username + ":" + password
  credentials_bytes = credentials.encode('ascii')
  base64_bytes = base64.b64encode(credentials_bytes)
  base64_message = base64_bytes.decode('ascii')

  headers = {
    'Authorization': 'Basic ' + base64_message
  }

  r = requests.get(url + '/secret', headers = headers)

  if r.status_code == 200:
    user = r.text
    serverMessage = ""
    return True
    
  else:
    serverMessage = r.text
    return False

def loginCookie(username, password):
  global user
  global serverMessage

  r = requests.post(url + '/login?username=' + username + '&password=' + password)

  if r.status_code == 200:
    user = r.text
    try:
      cookieFile = open("cookie.txt", "x")
      cookieFile.write(r.cookies["auth"])
      cookieFile.close()
    except IOError:
      cookieFile = open("cookie.txt", "w")
      cookieFile.write(r.cookies["auth"])
      cookieFile.close()

    serverMessage = ""
    return True
    
  else:
    serverMessage = r.text
    return False

def loginWithoutCredentials():
  global user
  try:
    cookieFile = open("cookie.txt", "r")
    headers = {
      'Cookie': 'auth=' + cookieFile.read()
    }
    cookieFile.close()
    x = requests.get(url + '/secret', headers = headers)
    
    if int(x.status_code) == 200:
      user = x.text
      return True 
      
    else:
      return False

  except IOError:
    return False

def register(username, password):
  global serverMessage
  global user

  credentials = username + ":" + password
  credentials_bytes = credentials.encode('ascii')
  base64_bytes = base64.b64encode(credentials_bytes)
  base64_message = base64_bytes.decode('ascii')

  headers = {
    'Authorization': 'Basic ' + base64_message
  }

  r = requests.post(url + '/register', headers = headers)

  if r.status_code == 200:
    user = r.text
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

  if not upToDate:
    checkMods()
  
  print("\nMODS:")

  for i in range(0, len(modList)):
    if i == selectedMod:
      print(colored("> ", "red"), modList[i])
    else:
      print("> " + modList[i])

def checkMods():
  r = requests.request("GET", url + '/upload')

  modIndexes = []
  for m in re.finditer('"', r.text):
    modIndexes.append(m.start())

  global modList
  modList = []

  for i in range(0, len(modIndexes)):
    if i % 2 == 1:
      modList.append(r.text[modIndexes[i - 1] + 1 : modIndexes[i]])
      # print("> " + r.text[modIndexes[i - 1] + 1 : modIndexes[i]])
  global upToDate
  upToDate = True


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



def uploadMod(path):
  splitString = path.split("/")
  filename = splitString[len(splitString) - 1]

  files=[
    ('avatar',(filename, open(path,'rb'),'application/java-archive'))
  ]

  # r = requests.post(url, files=files)

  payload = {}
  headers = {}

  r = requests.request("POST", url + '/upload', headers = headers, data = payload, files = files)

  # print(r.status_code)
  # print(r.text)

def downloadMod(modName):
  r = requests.request("GET", url + '/download' + "?mod=" + modName)
  # print(r.status_code)

  # downloadPath = "C:/Users/Joshua/AppData/Roaming/.minecraft/mods/"
  downloadPath = "./download/"

  try:
    file = open(downloadPath + modName, "xb")
    file.write(r.content)

  except IOError:
    file = open(downloadPath + modName, "wb")
    file.write(r.content)

def my_keyboard_hook(keyboard_event):
    global selectedMod
    global pressed
    global selectedCommand
    global enter
    global selectedLoginCommand
    global loginCommands
    # print("Name:", keyboard_event.name)
    # print("Scan code:", keyboard_event.scan_code)
    # print("Time:", keyboard_event.time)
    if pressed == False:
      if keyboard_event.scan_code == 72: #up
        if selectedMod > 0:
          selectedMod -= 1
        pressed = True

      if keyboard_event.scan_code == 80: #down
        if selectedMod < len(modList) - 1:
          selectedMod += 1
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

  running = True
  loggedIn = False
  keyboard.on_press(my_keyboard_hook)

  if loginWithoutCredentials():
    loggedIn = True

  while running:
    if (serverMessage != ""):
      print(serverMessage + "\n")

    if not loggedIn:

      printLoginCommands()
      
      while not pressed and not enter:
        pass
      pressed = False

      if selectedLoginCommand == 0 and enter == True:
        while msvcrt.kbhit():
          msvcrt.getch()

        sys.stdin.flush()
        username = input("Username: ")
        password = input("Password: ")
        if login(username, password):
          loggedIn = True
          serverMessage = ""
        enter = False

      elif selectedLoginCommand == 1 and enter == True:
        while msvcrt.kbhit():
          msvcrt.getch()
        username = input("Username: ")
        password = input("Password: ")
        if loginCookie(username, password):
          loggedIn = True
          serverMessage = ""
        enter = False

      elif selectedLoginCommand == 2 and enter == True:
        while msvcrt.kbhit():
          msvcrt.getch()
        username = input("Username: ")
        password = input("Password: ")
        if register(username, password):
          loggedIn = True
          serverMessage = ""
        enter = False
        
      elif selectedLoginCommand == 3 and enter == True:
        while msvcrt.kbhit():
          msvcrt.getch()
        username = input("Username: ")
        password = input("Password: ")
        deleteUser(username, password)
        enter = False

      elif selectedLoginCommand == 4 and enter == True:
        running = False

      os.system('cls')


    else:
      
      enter = False

      print("User: " + user)

      printMods()

      print()

      printCommands()

      
      while not pressed and not enter:
        pass

      pressed = False


      if selectedCommand == 0 and enter == True:
        enter = False
        # path = input("Enter mod directory:\n")
        path = askopenfilename()
        uploadMod(path)
        global upToDate
        upToDate = False

      elif selectedCommand == 1 and enter == True:
        enter = False
        downloadMod(modList[selectedMod])
        

      elif selectedCommand == 2 and enter == True:
        enter = False
        loggedIn = False
        try:
          os.remove("cookie.txt")
        except IOError:
          print("No cookie to remove")
        

      elif selectedCommand == 3 and enter == True:
        enter = False
        running = False
        
      

      os.system('cls')


main()