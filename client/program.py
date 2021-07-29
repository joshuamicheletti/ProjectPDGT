import requests
import base64
import re
import os
import keyboard
import msvcrt
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

choosingMods = False

commandsLength = 4

enter = False

def login(username, password):
  credentials = username + ":" + password
  credentials_bytes = credentials.encode('ascii')
  base64_bytes = base64.b64encode(credentials_bytes)
  base64_message = base64_bytes.decode('ascii')

  headers = {
    'Authorization': 'Basic ' + base64_message
  }

  x = requests.get(url + '/secret', headers = headers)

  if int(x.status_code) == 200:
    global user
    user = x.text
    return True
    
  else:
    print(x.status_code)
    print(x.text)
    return False

def loginCookie(username, password):
  x = requests.post(url + '/login?username=' + username + '&password=' + password)

  try:
    cookieFile = open("cookie.txt", "x")
    cookieFile.write(x.cookies["auth"])
    cookieFile.close()
  except IOError:
    cookieFile = open("cookie.txt", "w")
    cookieFile.write(x.cookies["auth"])
    cookieFile.close()

  if int(x.status_code) == 200:
    global user
    user = x.text
    return True
    
  else:
    print(x.status_code)
    print(x.text)
    return False

def loginWithoutCredentials():
  try:
    cookieFile = open("cookie.txt", "r")
    headers = {
      'Cookie': 'auth=' + cookieFile.read()
    }
    cookieFile.close()
    x = requests.get(url + '/secret', headers = headers)
    
    if int(x.status_code) == 200:
      global user
      user = x.text
      return True 
      
    else:
      return False

  except IOError:
    print("No cookie found")
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
  if selectedCommand == 0:
    print(colored("Upload mod", "red"), "  ", colored("Download mod", "white"), "  ", colored("LogOut", "white"), "  ", colored("Close", "white"), "\n")

  elif selectedCommand == 1:
    print(colored("Upload mod", "white"), "  ", colored("Download mod", "red"), "  ", colored("LogOut", "white"), "  ", colored("Close", "white"), "\n")

  elif selectedCommand == 2:
    print(colored("Upload mod", "white"), "  ", colored("Download mod", "white"), "  ", colored("LogOut", "red"), "  ", colored("Close", "white"), "\n")

  elif selectedCommand == 3:
    print(colored("Upload mod", "white"), "  ", colored("Download mod", "white"), "  ", colored("LogOut", "white"), "  ", colored("Close", "red"), "\n")



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
    # print("Name:", keyboard_event.name)
    # print("Scan code:", keyboard_event.scan_code)
    # print("Time:", keyboard_event.time)
    if keyboard_event.scan_code == 72:
      if selectedMod > 0:
        selectedMod -= 1
      pressed = True

    if keyboard_event.scan_code == 80:
      if selectedMod < len(modList) - 1:
        selectedMod += 1
      pressed = True

    if keyboard_event.scan_code == 75:
      if selectedCommand > 0:
        selectedCommand -= 1
      pressed = True

    if keyboard_event.scan_code == 77:
      if selectedCommand < commandsLength - 1:
        selectedCommand += 1
      pressed = True

    if keyboard_event.scan_code == 28:
      enter = True




def main():
  os.system('cls')
  running = True
  loggedIn = False
  keyboard.on_press(my_keyboard_hook)

  while running:
    if not loggedIn:
      if not loginWithoutCredentials():
        while msvcrt.kbhit():
          msvcrt.getch()
        command = int(input("Enter your Login Method: (1 - normal login, 2 - login with cookie, 0 - close)\n"))

        if command == 1:
          while msvcrt.kbhit():
            msvcrt.getch()
          username = input("Username: ")
          password = input("Password: ")
          if login(username, password):
            loggedIn = True

        elif command == 2:
          while msvcrt.kbhit():
            msvcrt.getch()
          username = input("Username: ")
          password = input("Password: ")
          if loginCookie(username, password):
            loggedIn = True
          
        elif command == 0:
          running = False

      else:
        loggedIn = True

      os.system('cls')


    else:
      global enter
      enter = False

      print("User: " + user)

      printMods()

      print()

      printCommands()

      global pressed
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
        while msvcrt.kbhit():
          msvcrt.getch()
        modName = input("Enter the mod you want to download:\n")
        downloadMod(modName)
        

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