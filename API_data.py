import requests
import json


#SportsPageFeeds API
def get_results(time):

    url = "https://sportspage-feeds.p.rapidapi.com/games"

    querystring = {"date":time,"league":"NBA","status":"final"}

    headers = {
        'x-rapidapi-key': "041e3a1151msh777ef8d0a2f1772p171c27jsn6932e0f4b92c",
        'x-rapidapi-host': "sportspage-feeds.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return json.loads(response.text)


#TheOddsApi
def get_odds(apikey):
    key = 'basketball_nba'
    response = requests.get('http://api.the-odds-api.com/v3/odds', params = {'api_key': apikey, 'sport': key, 'region': 'us', 'mkt': 'h2h'})
    json_data = json.loads(response.text)
    return json_data