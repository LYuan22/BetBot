import requests

url = "https://api-nba-v1.p.rapidapi.com/games/seasonYear/%7Bseasonyear%7D"

headers = {'x-rapidapi-host': 'api-nba-v1.p.rapidapi.com'}

response = requests.request("GET", url, headers=headers)

print(response.text)