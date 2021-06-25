import discord
import os
import requests
import json
import random
from dotenv import load_dotenv
from discord.ext import commands, tasks
from datetime import datetime #use this to tell how game ends with different API
import sqlite3
from Classes import Player, Bet, Game

#leaderboard
#adding money for merits or something idk - admin only command
#shut down command?
#change bets and members from dictionary to databases
#Figure out how to tell when game ends

client = discord.Client()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
apikey = os.getenv('api_key')
channelkey = int(os.getenv('channel'))


#creating dictionary of players, will wipe when bot is shut down. 
Players = {}
Games = []
Bets = []


conn = sqlite3.connect('players.db')
c = conn.cursor()
c.execute( """CREATE TABLE IF NOT EXISTS
players(playerid TEXT, money INTEGER, betwins INTEGER, betlosses INTEGER,
coinwins INTEGER, coinlosses INTEGER, revives INTEGER)""")
c.execute("""CREATE TABLE IF NOT EXISTS
bets(playerid TEXT, amount INTEGER, gameid INTEGER, team TEXT, betodds FLOAT)""")

def update_player_db(player):
    dict = {'id': player.get_id(), 'money': player.get_money(), 'betwins': player.get_betwins(),
                    'betlosses': player.get_betlosses(), 'coinwins': player.get_coinwins,
                    'coinlosses': player.get_coinlosses(), 'revives': player.get_revives()}
    with conn:
        c.execute("SELECT * from players WHERE playerid = :id", {'id': player.get_id()}) 
        if c.get == []:
            c.execute("INSERT INTO players VALUES (:id, :money, :betwins, :betlosses, :coinwins, :coinlosses, :revives)",
                    dict)
        else:
            c.execute("""UPDATE players SET money = :money, betwins = :betwins, betlosses = :betlosses,
                    coinwins = :coinwins, coinlosses = :coinlosses, revives = :revives WHERE id = :id""", dict)


def add_bet_db(bet):
    with conn:
        c.execute("INSERT INTO bets VALUES(:playerid, :amount, :gameid, :team, :betodds",
        {'playerid': bet.get_playerid(), 'amount': bet.get_amount(), 'gameid': bet.get_gameid(), 'team': bet.get_team(), 'betodds': bet.get_odds()})


def remove_bet_db(bet):
    with conn:
        c.execute("DELETE from players WHERE playerid = :playerid AND gameid = :gameid", {'playerid': bet.get_playerid(), 'gameid' : bet.get_gameid()})




#standard start event
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(channelkey)
    #await channel.send('ALIVE')
    test.start()


#message event
@client.event
async def on_message(message):
    if message.author == client.user:                   #checks that the bot isn't doing stuff on its own messages
        return


    content = message.content
    author = message.author
    name = author.name
    channel = message.channel
    word_arr = content.split()

    async def results(player, win, amount):
        if win == True:
            player.change_money(amount)
            await channel.send(name + ' has won $' + str(amount) + '. ' + name + ' now has $' + str(player.get_money()))
        else:
            player.change_money( -1 * amount)
            await channel.send(name + ' has lost $' + str(amount) + '. ' + name + ' now has $' + str(player.get_money()))

    if content.startswith('$revive'):
        temp_player = Players.get(author)
        if Players.get(author) != None:
            if temp_player.get_money() == 0:
                temp_player.revive()
                await channel.send('You have been revived with $500')
                Players[author] = temp_player
            else:
                await channel.send('You are not at $0, you do not need a revive')


    if content.startswith('$odds'):                        #prints odds
        for i in range(len(Games)):
            time = datetime.fromtimestamp(Games[i].get_time()).strftime("%m-%d-%y %H:%M")
            await channel.send(Games[i].get_hometeam() + ' vs ' + Games[i].get_awayteam() + '\n' +
                                str(time)+ '\n' +
                                str(Games[i].get_homeodds()) + '            ' + str(Games[i].get_awayodds()) + '\n') 
            #max 22 characters for team name

    elif content.startswith('$bet'):                      #initiates bet ($bet)
        if Players.get(author) == None:
            Players[author] = Player(author)
            await channel.send('sucks')



    elif content.startswith('$coinflip'):                 #coinflip ($coinflip [amount] [h/t])
        if ((len(word_arr)) != 3) or (word_arr[1].isnumeric() == False or (word_arr[2] == 'heads' or word_arr[2] == 'tails') == False):                               #format checker
            await channel.send('format: $coinflip amount heads/tails')
            return
        elif int(word_arr[1]) <= 0:
            await channel.send('amount cannot be 0 or negative')
            return
        val = int(word_arr[1])
        if Players.get(author) == None:                     #creates player if doesnt exist yet
            Players[author] = Player(author)
        temp_player = Players.get(author)
        if val > temp_player.get_money():
            await channel.send('You cannot bet more than you have')
            return


        toss = random.randint(0,1)
        if toss == 0:
            result = 'heads'
        elif toss == 1:
            result = 'tails'

        await channel.send(name + ' has flipped ' + result)
        if result == word_arr[2]:
            temp_player.add_coinwin()
        else:
            temp_player.add_coinloss()
        await results(temp_player, result == word_arr[2], val)
        Players[author] = temp_player
        update_player_db(temp_player)


    elif content.startswith('$stats'):
        if Players.get(author) == None:                     #creates player if doesnt exist yet
            Players[author] = Player(author)
        temp_player = Players.get(author)
        await channel.send(str(author) + ': \n' + 'Money: $' + str(temp_player.get_money()) + '\nBets Won: ' + str(temp_player.get_betwins()) + '\nBets Lost: ' + str(temp_player.get_betlosses()) + '\nBet Winrate: ' + str(temp_player.get_betwinrate())
                                    + '\nCoin Tosses Won: ' + str(temp_player.get_coinwins()) + '\nCoin Tosses Lost: ' + str(temp_player.get_coinlosses()) + '\nCoin Toss Winrate: ' + str(round((temp_player.get_coinwinrate() * 100), 2)) + '%'
                                    + '\nRevives: ' + str(temp_player.get_revives()))


def get_odds():
    key = 'basketball_nba'
    response = requests.get('http://api.the-odds-api.com/v3/odds', params = {'api_key': apikey, 'sport': key, 'region': 'us', 'mkt': 'h2h'})
    json_data = json.loads(response.text)
    return json_data

@tasks.loop(hours = 2)                                  #only 500 updates a month (not trying to pay to get more)
async def test():
    #apidata = get_odds()
    #channel = client.get_channel(channelkey)
    #await channel.send('Updating Odds')

    apidata = {'success': True, 'data': [{'id': '615244c04bcf4e42124695a65588b2dd', 'sport_key': 'basketball_nba', 'sport_nice': 'NBA', 'teams': ['Los Angeles Clippers', 'Phoenix Suns'], 'commence_time': 1624410600, 'home_team': 'Phoenix Suns',
    'sites': [{'site_key': 'bookmaker', 'site_nice': 'Bookmaker', 'last_update': 1624392595, 'odds': {'h2h': [2.55, 1.56]}},
    {'site_key': 'fanduel', 'site_nice': 'FanDuel', 'last_update': 1624392567, 'odds': {'h2h': [2.54, 1.54]}},
    {'site_key': 'betmgm', 'site_nice': 'BetMGM', 'last_update': 1624392527, 'odds': {'h2h': [2.55, 1.53]}},
    {'site_key': 'bovada', 'site_nice': 'Bovada', 'last_update': 1624392352, 'odds': {'h2h': [2.55, 1.57]}},
    {'site_key': 'williamhill_us', 'site_nice': 'William Hill (US)', 'last_update': 1624392464, 'odds': {'h2h': [2.65, 1.54]}},
    {'site_key': 'betonlineag', 'site_nice': 'BetOnline.ag', 'last_update': 1624392499, 'odds': {'h2h': [2.63, 1.54]}},
    {'site_key': 'gtbets', 'site_nice': 'GTbets', 'last_update': 1624392487, 'odds': {'h2h': [2.6, 1.53]}},
    {'site_key': 'sugarhouse', 'site_nice': 'SugarHouse', 'last_update': 1624392430,'odds': {'h2h': [2.55, 1.55]}},
    {'site_key': 'barstool', 'site_nice': 'Barstool Sportsbook', 'last_update': 1624392456, 'odds': {'h2h': [2.55, 1.55]}},
    {'site_key': 'betrivers', 'site_nice': 'BetRivers', 'last_update': 1624392466, 'odds': {'h2h': [2.55, 1.55]}},
    {'site_key': 'draftkings', 'site_nice': 'DraftKings', 'last_update': 1624392411, 'odds': {'h2h': [2.55, 1.55]}},
    {'site_key': 'unibet', 'site_nice': 'Unibet', 'last_update': 1624392550, 'odds': {'h2h': [2.55, 1.55]}},
    {'site_key': 'betfair', 'site_nice': 'Betfair', 'last_update': 1624392399, 'odds': {'h2h': [2.72, 1.57], 'h2h_lay': [2.74, 1.58]}},
    {'site_key': 'lowvig', 'site_nice': 'LowVig.ag', 'last_update': 1624392366, 'odds': {'h2h': [2.65, 1.53]}},
    {'site_key': 'caesars', 'site_nice': 'Caesars', 'last_update': 1624392481, 'odds': {'h2h': [2.65, 1.54]}},
    {'site_key': 'mybookieag', 'site_nice': 'MyBookie.ag', 'last_update': 1624392310, 'odds': {'h2h': [2.6, 1.53]}},
    {'site_key': 'foxbet', 'site_nice': 'FOX Bet', 'last_update': 1624392620, 'odds': {'h2h': [2.45, 1.53]}},
    {'site_key': 'intertops', 'site_nice': 'Intertops', 'last_update': 1624392598, 'odds': {'h2h': [2.65, 1.53]}}], 'sites_count': 18},
    
    {'id': '97984b72c5bd1b4e47594b79c1d105d8', 'sport_key': 'basketball_nba', 'sport_nice': 'NBA', 'teams': ['Atlanta Hawks', 'Milwaukee Bucks'], 'commence_time': 1624495200, 'home_team': 'Milwaukee Bucks',
    'sites': [{'site_key': 'fanduel', 'site_nice': 'FanDuel', 'last_update': 1624392567, 'odds': {'h2h': [3.8, 1.29]}},
    {'site_key': 'betfair', 'site_nice': 'Betfair', 'last_update': 1624392399, 'odds': {'h2h': [3.7, 1.35], 'h2h_lay': [3.9, 1.37]}},
    {'site_key': 'betmgm', 'site_nice': 'BetMGM', 'last_update': 1624392527, 'odds': {'h2h': [3.3, 1.36]}},
    {'site_key': 'betrivers', 'site_nice': 'BetRivers', 'last_update': 1624392466, 'odds': {'h2h': [3.35, 1.35]}},
    {'site_key': 'sugarhouse', 'site_nice': 'SugarHouse', 'last_update': 1624392430, 'odds': {'h2h': [3.35, 1.35]}},
    {'site_key': 'betonlineag', 'site_nice': 'BetOnline.ag', 'last_update': 1624392499, 'odds': {'h2h': [3.55, 1.32]}},
    {'site_key': 'barstool', 'site_nice': 'Barstool Sportsbook', 'last_update': 1624392456, 'odds': {'h2h': [3.35, 1.35]}},
    {'site_key': 'unibet', 'site_nice': 'Unibet', 'last_update': 1624392550, 'odds': {'h2h': [3.35, 1.35]}},
    {'site_key': 'williamhill_us', 'site_nice': 'William Hill (US)', 'last_update': 1624392464, 'odds': {'h2h': [3.55, 1.32]}},
    {'site_key': 'draftkings', 'site_nice': 'DraftKings', 'last_update': 1624392411, 'odds': {'h2h': [3.35, 1.35]}},
    {'site_key': 'lowvig', 'site_nice': 'LowVig.ag', 'last_update': 1624392366, 'odds': {'h2h': [3.55, 1.33]}},
    {'site_key': 'bovada', 'site_nice': 'Bovada', 'last_update': 1624392352, 'odds': {'h2h': [3.6, 1.31]}},
    {'site_key': 'gtbets', 'site_nice': 'GTbets', 'last_update': 1624392487, 'odds': {'h2h': [3.45, 1.32]}},
    {'site_key': 'foxbet', 'site_nice': 'FOX Bet', 'last_update': 1624392620, 'odds': {'h2h': [3.4, 1.3]}},
    {'site_key': 'caesars', 'site_nice': 'Caesars', 'last_update': 1624392481, 'odds': {'h2h': [3.6, 1.31]}},
    {'site_key': 'pointsbetus', 'site_nice': 'PointsBet (US)', 'last_update': 1624392488, 'odds': {'h2h': [3.4, 1.32]}},
    {'site_key': 'bookmaker', 'site_nice': 'Bookmaker', 'last_update': 1624392595, 'odds': {'h2h': [3.45, 1.33]}},
    {'site_key': 'mybookieag', 'site_nice': 'MyBookie.ag', 'last_update': 1624392310, 'odds': {'h2h': [3.5, 1.32]}},
    {'site_key': 'intertops', 'site_nice': 'Intertops', 'last_update': 1624392598, 'odds': {'h2h': [3.6, 1.31]}}], 'sites_count': 19}]}

    data = apidata.get('data')
    for i in range(len(data)):
        gamedata = data[i]
        sitedata = gamedata.get('sites')
        home_odds = 0
        away_odds = 0
        for j in range(len(sitedata)):
            h2hodds = sitedata[j].get('odds').get('h2h')
            home_odds = home_odds + h2hodds[1]
            away_odds = away_odds + h2hodds[0]
        home_odds = round(home_odds / len(sitedata), 2)
        away_odds = round(away_odds / len(sitedata), 2)

        #home_team_name = gamedata.get('teams')[1].split()
        #home_team_name = home_team_name[len(home_team_name) - 1]

        #away_team_name = gamedata.get('teams')[0].split()
        #away_team_name = away_team_name[len(away_team_name) - 1] #getting last word for all team (eg Atlanta Hawks -> Hawks, Los Angeles Lakers -> Lakers)

        game = Game(gamedata.get('id'), int(gamedata.get('commence_time')), gamedata.get('teams')[1], gamedata.get('teams')[0], home_odds, away_odds)
        Games.append(game)


client.run(TOKEN)