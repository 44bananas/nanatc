import requests
import json

parts = requests.get("https://api.warframe.market/v1/items").json()

with open('parts.txt', 'w') as data: 
     data.write(json.dumps(parts['payload']['items']))