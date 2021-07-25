import requests

url = "http://localhost:2000/upload"

r = requests.request("GET", url)

print(r.status_code)
print(r.text)