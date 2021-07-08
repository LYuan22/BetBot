import discord
import os
import random
from dotenv import load_dotenv
from discord.ext import tasks
import datetime
import sqlite3
from Classes import Player, Bet, Game
from API_data import get_results, get_odds

#leaderboard
#adding money for merits or something idk - admin only commands (also remove money)

#before new data is taken, check to see if a game has finished -> if it has go thorugh the bets for that specific game using gameid, and distribute money from there.

#Figure out how to tell when game ends


#Creates Dictionary of Games
Games = {}

client = discord.Client()

#Grab keys from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
apikey = os.getenv('api_key')
channelkey = int(os.getenv('channel'))


#Creating table for players
conn = sqlite3.connect('players.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS
players(playerid TEXT PRIMARY KEY, money INTEGER, betwins INTEGER, betlosses INTEGER,
coinwins INTEGER, coinlosses INTEGER, revives INTEGER)''')

#creating table for bets
c.execute('''CREATE TABLE IF NOT EXISTS
bets(amount INTEGER, gameid TEXT, team TEXT, betodds FLOAT, playerid TEXT)''')

#takes in id returns player with that id from database
def get_player_db(id):
    c.execute('SELECT * from players WHERE playerid = :id', {'id': id}) 
    data = c.fetchall()
    if data == ():
        return None
    else:
        player = data[0]
        return Player(player[0], player[1], player[2], player[3], player [4], player [5], player [6])

#send a player in to update/create player in database
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

#takes a gameid and returns all bets 
def get_game_bets_db(gameid):
    c.execute('SELECT * from bets WHERE gameid = :gameid', {'gameid': gameid})
    data = c.fetchall()
    list = []
    if data == ():
        return None
    else:
        for i in range(len(data)):
            inc = data[i]
            list.append(Bet(inc[4], inc[0], inc[1], inc[2], inc[3]))
        return list

#inserts a bet into the database
def add_bet_db(bet):
    with conn:
        c.execute('INSERT INTO bets VALUES(:amount, :gameid, :team, :betodds, :playerid)',
        {'playerid': bet.get_playerid(), 'amount': bet.get_amount(), 'gameid': bet.get_gameid(), 'team': bet.get_team(), 'betodds': bet.get_odds()}
        )

#removes a bet from the database (after bet has been completed)
def remove_bet_db(bet):
    with conn:
        c.execute('DELETE from bets WHERE playerid = :playerid AND gameid = :gameid AND amount = :amount AND team = :team',
        {'playerid': bet.get_playerid(), 'amount': bet.get_amount(), 'gameid': bet.get_gameid(), 'team': bet.get_team()})


#function to create a new player given an id
def new_player(id):
    return Player(id, 1000, 0, 0, 0, 0, 0)
    
#standard start event
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(channelkey)
    await channel.send('ALIVE')
    update_bets.start()
    update_odds.start()

#after money has been changed, print_results prints either win or lost money into discord
async def print_results(name, player, win, amount):
    channel = client.get_channel(channelkey)
    if win == True:
       await channel.send(name + ' has won $' + str(amount) + '. ' + name + ' now has $' + str(player.get_money()))
    else:
        await channel.send(name + ' has lost $' + str(amount) + '. ' + name + ' now has $' + str(player.get_money()))

#check is used to check if yes or no for bets
async def check(msg):
    return msg.author == c.author and msg.channel == c.channel and \
    msg.content.lower() in ['y', 'n']



#message event
@client.event
async def on_message(message):
    if message.author == client.user:                   #checks that the bot isn't doing stuff on its own messages
        return

    #gets all information from message
    content = message.content
    author = message.author
    authorid = str(author)
    name = author.name
    channel = message.channel
    word_arr = content.split()


    if content.startswith('$editmoney'): # ADMIN ONLY COMMAND $editmoney amount person
        if author.guild_permissions.administrator == True:
            if len(word_arr) != 3 or word_arr[1].isnumeric() == False or isinstance(word_arr[2], str) == False:
                await channel.send('format: $editmoney amount member')
                return
            else:
                amount = int(word_arr[1])
                member = word_arr[2]
                temp_player = get_player_db(member)
                if temp_player == None:
                    await channel.send('member does not exist')
                    return
                else:
                    temp_player.change_money(amount)
                    update_player_db(temp_player)
                    await channel.send('We have added ' + str(amount) + ' to ' + str(member) + '\'s account')
                    await channel.send(str(member) + ' now has ' + str(temp_player.get_money()))
        else:
            await channel.send('You do not have permissions for that command')
        
    #revives if $0
    elif content.startswith('$revive'):
        temp_player = get_player_db(authorid)
        if temp_player != None:
            if temp_player.get_money() == 0:
                temp_player.revive()
                await channel.send('You have been revived with $500')
                update_player_db(temp_player)
            else:
                await channel.send('You are not at $0, you do not need a revive')


    #prints odds with teams and time
    elif content.startswith('$odds'):
        g = list(Games.values())
        for i in range(len(g)):
            await channel.send(g[i].get_hometeam() + ' vs ' + g[i].get_awayteam() + '\n' +
                                str(g[i].get_homeodds()) + '                       ' + str(g[i].get_awayodds()) + '\n' +
                                'GameID: ' + g[i].get_gameid() + '\n' + 
                                str(datetime.datetime.fromtimestamp(g[i].get_time()).strftime('%m-%d-%y   %H:%M'))+ '\n') 




    #initiates bet ($bet amount gameid team)
    elif content.startswith('$bet'): 
        
        if len(word_arr) != 4 or word_arr[1].isnumeric() == False or isinstance(word_arr[2], str) == False or isinstance(word_arr[3], str) == False:
            await channel.send('format: $bet amount gameid team')
            return
        elif int(word_arr [1]) <= 0:
            await channel.send('amount cannot be 0 or negative')
            return

        gameid = word_arr[2]
        game = Games.get(gameid)
        team = word_arr[3]


        amount = int(word_arr[1])
        temp_player = get_player_db(authorid)
        if temp_player == None:
            temp_player = new_player(authorid)
        if amount > temp_player.get_money():      #checks you can bet the amount
            await channel.send('You cannot bet more than you have')
            return
        

        def check(msg):
            return msg.author == author and msg.channel == channel and msg.content.lower() in ['y', 'n']


        hometeam = game.get_hometeam().split()
        hometeam = hometeam[len(hometeam) - 1]
        awayteam = game.get_awayteam().split()
        awayteam = awayteam[len(awayteam) - 1]

        if game == None:
            await channel.send('Invalid Gameid')
            return
        elif team == hometeam:
            await channel.send('Are you sure you want to place a bet on ' + team + ' for ' + str(amount) + '? [y/n]')
            msg = await client.wait_for('message', check = check)
            if msg.content.lower() == 'y':
                bet = Bet(authorid, amount, gameid, game.get_hometeam(), game.get_homeodds())
            else:
                await channel.send('Bet has not been confirmed')
                return
        elif team == awayteam:
            await channel.send('Are you sure you want to place a bet on ' + team + ' for ' + str(amount) + '? [y/n]')
            msg = await client.wait_for('message', check = check)
            if msg.content.lower() == 'y':
                bet = Bet(authorid, amount, gameid, game.get_awayteam(), game.get_homeodds())
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





    #coinflip ($coinflip [amount] [h/t])
    elif content.startswith('$coinflip'):
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



    #prints stats in discord
    elif content.startswith('$stats'):
        temp_player = get_player_db(authorid)
        if temp_player == None:                     #creates player if doesnt exist yet
            temp_player = new_player(author)
        await channel.send(str(author) + ': \n' + 'Money: $' + str(temp_player.get_money()) + '\nBets Won: ' + str(temp_player.get_betwins()) + '\nBets Lost: ' + str(temp_player.get_betlosses()) + '\nBet Winrate: ' + str(temp_player.get_betwinrate())
                                    + '\nCoin Tosses Won: ' + str(temp_player.get_coinwins()) + '\nCoin Tosses Lost: ' + str(temp_player.get_coinlosses()) + '\nCoin Toss Winrate: ' + str(round((temp_player.get_coinwinrate() * 100), 2)) + '%'
                                    + '\nRevives: ' + str(temp_player.get_revives()))

#only 500 updates a month (not trying to pay to get more)
@tasks.loop(hours = 2)      
async def update_odds():
    api_odds_data = get_odds(apikey)
    channel = client.get_channel(channelkey)
    await channel.send('Updating Odds')

    #grabbing data from TheOddsApi
    data = api_odds_data.get('data')
    for i in range(len(data)):
        gamedata = data[i]
        sitedata = gamedata.get('sites')
        home_odds = 0
        away_odds = 0
        for j in range(len(sitedata)):
            h2hodds = sitedata[j].get('odds').get('h2h')
            home_odds += h2hodds[1]
            away_odds += h2hodds[0]
        home_odds = round(home_odds / len(sitedata), 2)
        away_odds = round(away_odds / len(sitedata), 2)
        Games[gamedata.get('id')] = Game(gamedata.get('id'), int(gamedata.get('commence_time')), gamedata.get('teams')[1], gamedata.get('teams')[0], home_odds, away_odds)




@tasks.loop(hours = 2)
async def update_bets():
    channel = client.get_channel(channelkey)

    current_time = datetime.datetime.now()
    current_time = current_time.strftime('%Y-%m-%d')
    api_results_data = get_results(current_time)

    g = list(Games.values())
    bets = []
    #Getting data from Sportspage API
    game_results = api_results_data.get('results')


    #Loop checks if games are finished
    for i in range(len(game_results)):
        for j in range(len(g)):
            time = datetime.datetime.strptime(game_results[i].get('schedule').get('date')[0:10], '%Y-%m-%d')
            time -= datetime.timedelta(days = 1)
            time = str(time)[0:10]
            if time == datetime.datetime.fromtimestamp(g[j].get_time()).strftime('%Y-%m-%d'):
                teams = game_results[i].get('teams')
                if teams.get('away').get('team') == g[j].get_awayteam():
                    if teams.get('home').get('team') == g[j].get_hometeam():
                        score = game_results[i].get('scoreboard').get('score')
                        if score.get('away') < score.get('home'):
                            g[j].change_result(1)
                            Games[g[j].get_gameid] = g[j] 
                        else:
                            g[j].change_result(2)

    #Gets all bets for finished games
    for i in range(len(g)):
        game = g[i]
        if game.get_result() != 0:
            bets += list(get_game_bets_db(game.get_gameid()))


    #allots money based on finished games, removes bets
    for i in range(len(bets)):                                      
        bet = bets[i]
        gameid = bet.get_gameid()
        temp_player = get_player_db(bet.get_playerid())
        val = bet.get_amount() * (1 + bet.get_odds())
        playerid = temp_player.get_id()

        if Games[gameid].get_result() == 1 and bet.get_team() == Games[gameid].get_hometeam():
            temp_player.change_money(val)
            await channel.send(playerid + ' has won ' + str(val) + ' betting on ' + bet.get_team())
        elif Games[gameid].get_result() == 2 and bet.get_team() == Games[gameid].get_awayteam():
            temp_player.change_money(val)
            await channel.send(playerid + ' has won ' + str(val) + ' betting on ' + bet.get_team())
        else:
            await channel.send(playerid + ' has lost ' + bet.amount() + ' betting on ' + bet.get_team())
        update_player_db(temp_player)
        remove_bet_db(bet)


client.run(TOKEN)