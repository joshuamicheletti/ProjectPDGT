import requests
import json
import base64

def checkItems():
  x = requests.get('https://projectpdgt.herokuapp.com/people')
  # print(x)
  y = json.loads(x.text)

  for i in range(len(y)):
    print(str(y[i]["id"]) + "> " + y[i]["name"] + " " + y[i]["surname"])


def deleteItems(target):
  x = requests.delete('https://projectpdgt.herokuapp.com/people/' + str(target))
  # print(x.text)

def postItem(newItem):
  headers = {
    'Content-Type': 'application/json'
  }
  # data = "{\n  \"name\": \"Pippo\",\n  \"surname\": \"Micheletti\"\n}"
  response = requests.request(
    'POST',
    'https://projectpdgt.herokuapp.com/people?username=joshua&password=password',
    data=newItem,
    headers=headers,
  )
  
  print(response.text)


def login(username, password):

  credentials = username + ":" + password
  credentials_bytes = credentials.encode('ascii')
  base64_bytes = base64.b64encode(credentials_bytes)
  base64_message = base64_bytes.decode('ascii')

  print(base64_message)

  headers = {
    'Authorization': 'Basic ' + base64_message
  }

  x = requests.get('https://projectpdgt.herokuapp.com/secret', headers = headers)

  print(x.text)


def loginCookie(username, password):
  x = requests.post('https://projectpdgt.herokuapp.com/login?username=' + username + '&password=' + password)

  print(x.cookies["auth"])

  return x.cookies["auth"]

def loginWithoutCredentials(cookie):
  headers = {
    'Cookie': 'auth=' + cookie
  }
  x = requests.get('https://projectpdgt.herokuapp.com/secret', headers = headers)
  print(x.text)


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
      checkItems()

      if cookie != 0:
        print(cookie)

      command = int(input("Enter your action: (1 - add an item, 2 - remove an item, 0 - close)\n"))

      if command == 1:
        name = input("Enter the name: ")
        surname = input("Enter the surname: ")

        data = "{\n  \"name\": \"" + name + "\",\n  \"surname\": \"" + surname + "\"\n}"

        postItem(data)

      elif command == 2:
        target = int(input("Enter the element you want to delete: "))
        deleteItems(target)

      elif command == 3:
        #send file
        files = {'upload_file': open('../mod.jar','rb')}
        response = requests.post('https://projectpdgt.herokuapp.com/people', files=files)
        print(response.text)


      elif command == 0:
        running = False


  # checkItems()
  # newItem = "{\n  \"name\": \"Pippo\",\n  \"surname\": \"Micheletti\"\n}"
  # postItem(newItem)
  # checkItems()
  # # deleteItem()
  
  # cookie = loginCookie()

  # loginWithoutCredentials(cookie)
  # # loginWithoutCredentials()




main()




