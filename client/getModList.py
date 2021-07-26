import requests

url = "https://projectpdgt.herokuapp.com/upload"
# url = "http://localhost:2000/upload"

r = requests.request("GET", url)

print(r.status_code)
print(r.text)