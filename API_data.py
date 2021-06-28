import requests
import json
import datetime

def get_games(time):

    url = "https://sportspage-feeds.p.rapidapi.com/games"

    querystring = {"date":"2021-06-22","league":"NBA","status":"final"}

    headers = {
        'x-rapidapi-key': "041e3a1151msh777ef8d0a2f1772p171c27jsn6932e0f4b92c",
        'x-rapidapi-host': "sportspage-feeds.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response

def get_odds(apikey):
    key = 'basketball_nba'
    response = requests.get('http://api.the-odds-api.com/v3/odds', params = {'api_key': apikey, 'sport': key, 'region': 'us', 'mkt': 'h2h'})
    json_data = json.loads(response.text)
    return json_data