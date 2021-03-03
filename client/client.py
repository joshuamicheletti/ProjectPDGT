import requests
import json

def checkItems():
  x = requests.get('https://projectpdgt.herokuapp.com/people')
  print(x)
  y = json.loads(x.text)

  for i in range(len(y)):
    print("> " + y[i]["name"] + " " + y[i]["surname"])


def deleteItems(target):
  x = requests.delete('https://projectpdgt.herokuapp.com/people/' + str(target))
  print(x.text)


def main():
  checkItems()
  deleteItems(2)
  checkItems()


main()




