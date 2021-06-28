import discord
import os
import requests
import json
import random
from dotenv import load_dotenv
from discord.ext import tasks
import datetime #use this to tell how game ends with different API
import sqlite3
from Classes import Player, Bet, Game
from API_data import get_games, get_odds

#leaderboard
#adding money for merits or something idk - admin only commands (also remove money)

#before new data is taken, check to see if a game has finished -> if it has go thorugh the bets for that specific game using gameid, and distribute money from there.

#Figure out how to tell when game ends

client = discord.Client()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
apikey = os.getenv('api_key')
channelkey = int(os.getenv('channel'))


#creating dictionary of players, will wipe when bot is shut down. 
Games = {}
Bets = []

conn = sqlite3.connect('players.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS
players(playerid TEXT PRIMARY KEY, money INTEGER, betwins INTEGER, betlosses INTEGER,
coinwins INTEGER, coinlosses INTEGER, revives INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS
bets(amount INTEGER, gameid TEXT, team TEXT, betodds FLOAT, playerid TEXT)''')

def get_player_db(id):
    c.execute('SELECT * from players WHERE playerid = :id', {'id': id}) 
    data = c.fetchall()
    if data == []:
        return None
    else:
        player = data[0]
        return Player(player[0], player[1], player[2], player[3], player [4], player [5], player [6])

def update_player_db(player):
    dict = {'id': str(player.get_id()), 'money': player.get_money(), 'betwins': player.get_betwins(),
                    'betlosses': player.get_betlosses(), 'coinwins': player.get_coinwins(),
                    'coinlosses': player.get_coinlosses(), 'revives': player.get_revives()}
    with conn:

        c.execute('SELECT * from players WHERE playerid = :id', dict) 
        if c.fetchall() == []:
            c.execute('INSERT INTO players VALUES (:id, :money, :betwins, :betlosses, :coinwins, :coinlosses, :revives)',
                    dict)
        else:
            c.execute('''UPDATE players SET money = :money, betwins = :betwins, betlosses = :betlosses,
                    coinwins = :coinwins, coinlosses = :coinlosses, revives = :revives WHERE playerid = :id''', dict)


def get_game_bet_db(gameid):
    c.execute('SELECT * from bets WHERE gameid = :gameid', {'gameid': gameid})
    return c.fetchall()

def add_bet_db(bet):
    with conn:
        c.execute('INSERT INTO bets VALUES(:amount, :gameid, :team, :betodds, :playerid)',
        {'playerid': bet.get_playerid(), 'amount': bet.get_amount(), 'gameid': bet.get_gameid(), 'team': bet.get_team(), 'betodds': bet.get_odds()}
        )

def remove_bet_db(bet):
    with conn:
        c.execute('DELETE from players WHERE playerid = :playerid AND gameid = :gameid', {'playerid': bet.get_playerid(), 'gameid' : bet.get_gameid()})



def new_player(id):
    return Player(id, 1000, 0, 0, 0, 0, 0)
    
#standard start event
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(channelkey)
    #await channel.send('ALIVE')
    update.start()

async def print_results(name, player, win, amount):
    channel = client.get_channel(channelkey)
    if win == True:
       await channel.send(name + ' has won $' + str(amount) + '. ' + name + ' now has $' + str(player.get_money()))
    else:
        await channel.send(name + ' has lost $' + str(amount) + '. ' + name + ' now has $' + str(player.get_money()))

async def check(msg):
    return msg.author == c.author and msg.channel == c.channel and \
    msg.content.lower() in ['y', 'n']



#message event
@client.event
async def on_message(message):
    if message.author == client.user:                   #checks that the bot isn't doing stuff on its own messages
        return


    content = message.content
    author = message.author
    authorid = str(author)
    name = author.name
    channel = message.channel
    word_arr = content.split()
    print(author.guild_permissions.administrator)

    if content.startswith('$editmoney'): # ADMIN ONLY COMMAND $editmoney amount person
        if author.guild_permissions.administrator == True:
            if len(word_arr) != 3 or word_arr[1].isnumeric() == False or isinstance(word_arr[2], str) == False:
                await channel.send('format: $editmoney amount member')
                return
            else:
                amount = word_arr[1] 
                member = word_arr[2]
                temp_player = get_player_db(member)
                if temp_player == None:
                    await channel.send('member does not exist')
                    return
                else:
                    temp_player.change_money(amount)
                update_player_db(temp_player)
        else:
            await channel.send('You do not have permissions for that command')
        

    elif content.startswith('$revive'):
        temp_player = get_player_db(authorid)
        if temp_player != None:
            if temp_player.get_money() == 0:
                temp_player.revive()
                await channel.send('You have been revived with $500')
                update_player_db(temp_player)
            else:
                await channel.send('You are not at $0, you do not need a revive')


    elif content.startswith('$odds'):                        #prints odds with teams and time
        g = list(Games.values())
        print(g)
        for i in range(len(g)):
            await channel.send(g[i].get_hometeam() + ' vs ' + g[i].get_awayteam() + '\n' +
                                'Gameid: ' + g[i].get_gameid() + '\n' + 
                                #str(datetime.fromtimestamp(Games[i].get_time()).strftime('%m-%d-%y   %H:%M'))+ '\n' +
                                str(g[i].get_homeodds()) + '            ' + str(g[i].get_awayodds()) + '\n\n') 
            #max 22 characters for team name






    elif content.startswith('$bet'):                      #initiates bet ($bet amount gameid team)
        
        if len(word_arr) != 4 or word_arr[1].isnumeric() == False or isinstance(word_arr[2], str) == False or isinstance(word_arr[3], str) == False:
            await channel.send('format: $bet amount gameid team')
            return
        elif int(word_arr [1]) <= 0:
            await channel.send('amount cannot be 0 or negative')
            return

        gameid = word_arr[2]
        game = Games.get(gameid)
        team = word_arr[3]

        hometeam = game.get_hometeam().split()
        hometeam = hometeam[len(hometeam) - 1]
        awayteam = game.get_awayteam().split()
        awayteam = awayteam[len(awayteam) - 1]

        amount = int(word_arr[1])
        temp_player = get_player_db(authorid)
        if temp_player == None:
            temp_player = new_player(authorid)
        if amount > temp_player.get_money():      #checks you can bet the amount
            await channel.send('You cannot bet more than you have')
            return
        

        def check(msg):
            return msg.author == author and msg.channel == channel and msg.content.lower() in ['y', 'n']

        if game == None:
            await channel.send('Invalid Gameid')
            return
        elif team == hometeam:
            await channel.send('Are you sure you want to place a bet on ' + team + ' for ' + str(amount) + '? [y/n]')
            msg = await client.wait_for('message', check = check)
            if msg.content.lower() == 'y':
                bet = Bet(authorid, amount, gameid, team, game.get_homeodds())
            else:
                await channel.send('Bet has not been confirmed')
                return
        elif team == awayteam:
            await channel.send('Are you sure you want to place a bet on ' + team + ' for ' + str(amount) + '? [y/n]')
            msg = await client.wait_for('message', check = check)
            if msg.content.lower() == 'y':
                bet = Bet(authorid, amount, gameid, team, game.get_homeodds())
            else:
                await channel.send('Bet has not been confirmed')
                return
        else:
            await channel.send('Not a team in that game')
            return

        temp_player.change_money(-1 * amount)
        update_player_db(temp_player)
        add_bet_db(bet)
        await channel.send('Your bet on  ' + team + ' for ' + str(amount) + ' has been confimed.')






    elif content.startswith('$coinflip'):                 #coinflip ($coinflip [amount] [h/t])
        if ((len(word_arr)) != 3) or word_arr[1].isnumeric() == False or (word_arr[2] == 'heads' or word_arr[2] == 'tails') == False:                               #format checker
            await channel.send('format: $coinflip amount heads/tails')
            return
        elif int(word_arr[1]) <= 0:
            await channel.send('amount cannot be 0 or negative')
            return
        
        amount = int(word_arr[1])
        temp_player = get_player_db(authorid)
        if temp_player == None:                     #creates player if doesnt exist yet
            temp_player = new_player(authorid)

        if amount > temp_player.get_money():      #checks you can bet the amount
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
            temp_player.change_money(amount)
        else:
            temp_player.add_coinloss()
            temp_player.change_money( -1 * amount)
        await print_results(name, temp_player, result == word_arr[2], amount)
        update_player_db(temp_player)




    elif content.startswith('$stats'):
        temp_player = get_player_db(authorid)
        if temp_player == None:                     #creates player if doesnt exist yet
            temp_player = new_player(author)
        await channel.send(str(author) + ': \n' + 'Money: $' + str(temp_player.get_money()) + '\nBets Won: ' + str(temp_player.get_betwins()) + '\nBets Lost: ' + str(temp_player.get_betlosses()) + '\nBet Winrate: ' + str(temp_player.get_betwinrate())
                                    + '\nCoin Tosses Won: ' + str(temp_player.get_coinwins()) + '\nCoin Tosses Lost: ' + str(temp_player.get_coinlosses()) + '\nCoin Toss Winrate: ' + str(round((temp_player.get_coinwinrate() * 100), 2)) + '%'
                                    + '\nRevives: ' + str(temp_player.get_revives()))


@tasks.loop(hours = 2)                                  #only 500 updates a month (not trying to pay to get more)
async def update():
    #apidata = get_odds(apikey)
    #channel = client.get_channel(channelkey)
    #await channel.send('Updating Odds')
    gamedata = {"status":200,
    "time":"2021-06-28T21:17:52.426Z",
    "games":1,"skip":0,
    "results":[
        {"schedule":{"date":"2021-06-23T01:00:00.000Z","tbaTime":False},
        "summary":"Los Angeles Clippers @ Phoenix Suns",
        "details":{"league":"NBA","seasonType":"postseason","season":2020,"conferenceGame":True,"divisionGame":True},
        "status":"final",
        "teams":{"away":{"team":"Los Angeles Clippers","location":"Los Angeles","mascot":"Clippers","abbreviation":"LAC","conference":"Western","division":"Pacific"},"home":{"team":"Phoenix Suns","location":"Phoenix","mascot":"Suns","abbreviation":"PHX","conference":"Western","division":"Pacific"}},
        "lastUpdated":"2021-06-23T04:04:50.076Z",
        "gameId":264995,
        "venue":{"name":"Phoenix Suns Arena","city":"Phoenix","state":"AZ","neutralSite":False},
        "odds":[{"spread":{"open":{"away":6,"home":-6,"awayOdds":-115,"homeOdds":-105},"current":{"away":4.5,"home":-4.5,"awayOdds":-110,"homeOdds":-115}},"moneyline":{"open":{"awayOdds":199,"homeOdds":-239},"current":{"awayOdds":165,"homeOdds":-188}},"total":{"open":{"total":224,"overOdds":-110,"underOdds":-110},"current":{"total":223,"overOdds":-110,"underOdds":-110}},"openDate":"2021-06-21T13:14:00.367Z","lastUpdated":"2021-06-23T01:16:58.737Z"}],
        "scoreboard":{"score":{"away":103,"home":104,"awayPeriods":[22,25,24,32],"homePeriods":[25,23,27,29]},"currentPeriod":4,"periodTimeRemaining":"0:00"}}]}
    gamedata.get('results')[0].get('scoreboard').get('score').get('home')



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
        Games[gamedata.get('id')] = Game(gamedata.get('id'), int(gamedata.get('commence_time')), gamedata.get('teams')[1], gamedata.get('teams')[0], home_odds, away_odds)

client.run(TOKEN)