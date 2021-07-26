import requests

url = "https://projectpdgt.herokuapp.com/upload"
# url = "http://localhost:2000/upload"

# files = ('avatar', ('mod.jar', open('../mod.jar', 'rb')))
files=[
  ('avatar',('mod.jar',open('../modsToUpload/mod.jar','rb'),'application/java-archive'))
]

# r = requests.post(url, files=files)

payload = {}
headers = {}

r = requests.request("POST", url, headers = headers, data = payload, files = files)

print(r.status_code)
print(r.text)
print("ciao")