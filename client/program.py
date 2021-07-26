import requests
import base64
import re

url = "https://projectpdgt.herokuapp.com"

def login(username, password):

  credentials = username + ":" + password
  credentials_bytes = credentials.encode('ascii')
  base64_bytes = base64.b64encode(credentials_bytes)
  base64_message = base64_bytes.decode('ascii')

  print(base64_message)

  headers = {
    'Authorization': 'Basic ' + base64_message
  }

  x = requests.get(url + '/secret', headers = headers)

  print(x.text)

def loginCookie(username, password):
  x = requests.post(url + '/login?username=' + username + '&password=' + password)

  print(x.cookies["auth"])

  return x.cookies["auth"]

def loginWithoutCredentials(cookie):
  headers = {
    'Cookie': 'auth=' + cookie
  }
  x = requests.get(url + '/secret', headers = headers)
  print(x.text)


def checkMods():
  
  r = requests.request("GET", url + '/upload')

  modIndexes = []
  for m in re.finditer('"', r.text):
    modIndexes.append(m.start())

  print()

  for i in range(0, len(modIndexes)):
    if i % 2 == 1:
      print(r.text[modIndexes[i - 1] + 1 : modIndexes[i]])

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

  print(r.status_code)
  print(r.text)

def downloadMod(modName):
  r = requests.request("GET", url + '/download')
  print(r.status_code)

  downloadPath = "C:\Users\Joshua\AppData\Roaming\.minecraft\mods"
  modName0 = "Xaeros_Minimap_21.10.0.3_Forge_1.16.5.jar"

  file = open(downloadPath + modName0, "xb")

  file.write(r.content)


def main():
  running = True
  cookie = 0
  loggedIn = False

  while running:
    if not loggedIn:
      command = int(input("Enter your Login Method: (1 - normal login, 2 - login with cookie, 0 - close)\n"))

      if command == 1:
        username = input("Username: ")
        password = input("Password: ")
        login(username, password)
        loggedIn = True

      elif command == 2:
        username = input("Username: ")
        password = input("Password: ")
        cookie = loginCookie(username, password)
        loggedIn = True

      elif command == 0:
        running = False

    else:
      if cookie != 0:
        print(cookie)

      checkMods()

      command = int(input("Enter your action: (1 - upload a mod, 2 - download a mod, 0 - close)\n"))

      if command == 1:
        path = input("Enter mod directory:\n")
        uploadMod(path)

      elif command == 2:
        modName = input("Enter the mod you want to download:\n")
        downloadMod(modName)


      elif command == 0:
        running = False


main()