import requests
import json


#SportsPageFeeds API
def get_results(results_key, time):

    url = "https://sportspage-feeds.p.rapidapi.com/games"

    querystring = {"date":time,"league":"NBA","status":"final"}

    headers = {
        'x-rapidapi-key': results_key,
        'x-rapidapi-host': "sportspage-feeds.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return json.loads(response.text)


#TheOddsApi
def get_odds(odds_key):
    key = 'basketball_nba'
    response = requests.get('http://api.the-odds-api.com/v3/odds', params = {'api_key': odds_key, 'sport': key, 'region': 'us', 'mkt': 'h2h'})
    json_data = json.loads(response.text)
    return json_data