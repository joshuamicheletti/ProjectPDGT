import requests
import base64
import re
import os

url = "https://projectpdgt.herokuapp.com"
# url = "http://localhost:2000"

user = ""

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


def checkMods():
  r = requests.request("GET", url + '/upload')

  modIndexes = []
  for m in re.finditer('"', r.text):
    modIndexes.append(m.start())

  print("\nMODS:")

  for i in range(0, len(modIndexes)):
    if i % 2 == 1:
      print("> " + r.text[modIndexes[i - 1] + 1 : modIndexes[i]])

  print()

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


def main():
  running = True
  loggedIn = False

  while running:
    if not loggedIn:
      if not loginWithoutCredentials():
        command = int(input("Enter your Login Method: (1 - normal login, 2 - login with cookie, 0 - close)\n"))

        if command == 1:
          username = input("Username: ")
          password = input("Password: ")
          if login(username, password):
            loggedIn = True

        elif command == 2:
          username = input("Username: ")
          password = input("Password: ")
          if loginCookie(username, password):
            loggedIn = True
          
        elif command == 0:
          running = False

      else:
        loggedIn = True

    else:
      print("\nUser: " + user)

      checkMods()

      command = int(input("Enter your action: (1 - upload a mod, 2 - download a mod, 3 - LogOut, 0 - close)\n"))

      if command == 1:
        path = input("Enter mod directory:\n")
        uploadMod(path)

      elif command == 2:
        modName = input("Enter the mod you want to download:\n")
        downloadMod(modName)

      elif command == 3:
        loggedIn = False
        try:
          os.remove("cookie.txt")
        except IOError:
          print("No cookie to remove")

      elif command == 0:
        running = False


main()