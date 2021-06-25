class Player:
    def __init__(self, id):
        self.money = 1000
        self.id = id
        self.betwins = 0
        self.betlosses = 0
        self.coinwins = 0
        self.coinlosses = 0
        self.revives = 0

    def get_id(self):
        return self.id

    def get_money(self):
        return self.money
    def change_money(self, amount):
        self.money = self.money + amount


    def add_betloss(self):
        self.betlosses += 1
    def add_betwin(self):
        self.betwins += 1
    def get_betwinrate(self):
        total = self.betwins + self.betlosses
        if (total == 0):
            return 0
        else:
            return self.betwins / total
    def get_betwins(self):
        return self.betwins
    def get_betlosses(self):
        return self.betlosses


    def add_coinwin(self):
        self.coinwins += 1
    def add_coinloss(self):
        self.coinlosses += 1
    def get_coinwins(self):
        return self.coinwins
    def get_coinlosses(self):
        return self.coinlosses
    def get_coinwinrate(self):
        total = self.coinwins + self.coinlosses
        if (total == 0):
            return 0
        else:
            return self.coinwins / total

    def revive(self):
        self.money = 500
        self.revives += 1
    def get_revives(self):
        return self.revives

class Bet:
    def __init__(self, playerid, amount, gameid, team, odds):
        self.amount = amount
        self.playerid = playerid
        self.gameid = gameid
        self.odds = odds
        self.team = team

    def get_playerid(self):
        return self.playerid
    def get_gameid(self):
        return self.gameid
    def get_odds(self):
        return self.odds
    def get_amount(self):
        return self.amount
    def get_team(self):
        return self.team

class Game:
    def __init__(self, id, time, home_team, away_team, home_odds, away_odds):
        self.id = id
        self.time = time
        self.home_team = home_team
        self.away_team = away_team
        self.home_odds = home_odds
        self.away_odds = away_odds
        self.result = 0
    def get_id(self):
        return self.id
    def get_time(self):
        return self.time
    def get_hometeam(self):
        return self.home_team
    def get_awayteam(self):
        return self.away_team
    def get_homeodds(self):
        return self.home_odds
    def get_awayodds(self):
        return self.away_odds
    def get_result(self):
        return self.result
    def change_result(self, result): #1 for home team, 2 for away team, 0 for no result yet
        self.result = result