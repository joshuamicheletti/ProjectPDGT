import requests
import io

# url = "https://projectpdgt.herokuapp.com/upload"
url = "http://localhost:2000/download"

r = requests.request("GET", url)


print(r.status_code)

file = open("download/Xaeros_Minimap_21.10.0.3_Forge_1.16.5.jar", "xb")

# file = io.open("download/mod.jar", "x", encoding="utf-8")

file.write(r.content)
