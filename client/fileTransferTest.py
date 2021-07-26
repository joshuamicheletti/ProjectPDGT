import requests

# url = "https://projectpdgt.herokuapp.com/upload"
url = "http://localhost:2000/upload"

fileName = "Xaeros_Minimap_21.10.0.3_Forge_1.16.5.jar"
directory = "./"

# files = ('avatar', ('mod.jar', open('../mod.jar', 'rb')))
files=[
  ('avatar',(fileName,open(directory + fileName,'rb'),'application/java-archive'))
]

# r = requests.post(url, files=files)

payload = {}
headers = {}

r = requests.request("POST", url, headers = headers, data = payload, files = files)

print(r.status_code)
print(r.text)
print("ciao")