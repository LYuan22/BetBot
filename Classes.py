class Player:
    def __init__(self, id, money, betwins, betlosses, coinwins, coinlosses, revives):
        self.__id = id
        self.__money = money
        self.__betwins = betwins
        self.__betlosses = betlosses
        self.__coinwins = coinwins
        self.__coinlosses = coinlosses
        self.__revives = revives

    def get_id(self):
        return self.__id

    def get_money(self):
        return self.__money
    def change_money(self, __amount):
        self.__money = self.__money + __amount


    def add_betloss(self):
        self.__betlosses += 1
    def add_betwin(self):
        self.__betwins += 1
    def get_betwinrate(self):
        total = self.__betwins + self.__betlosses
        if (total == 0):
            return 0
        else:
            return self.__betwins / total
    def get_betwins(self):
        return self.__betwins
    def get_betlosses(self):
        return self.__betlosses


    def add_coinwin(self):
        self.__coinwins += 1
    def add_coinloss(self):
        self.__coinlosses += 1
    def get_coinwins(self):
        return self.__coinwins
    def get_coinlosses(self):
        return self.__coinlosses
    def get_coinwinrate(self):
        total = self.__coinwins + self.__coinlosses
        if (total == 0):
            return 0
        else:
            return self.__coinwins / total

    def revive(self):
        self.__money = 500
        self.__revives += 1
    def get_revives(self):
        return self.__revives

class Bet:
    def __init__(self, playerid, amount, gameid, team, odds):
        self.__amount = amount
        self.__playerid = playerid
        self.__gameid = gameid
        self.__odds = odds
        self.__team = team

    def get_playerid(self):
        return self.__playerid
    def get_gameid(self):
        return self.__gameid
    def get_odds(self):
        return self.__odds
    def get_amount(self):
        return self.__amount
    def get_team(self):
        return self.__team

class Game:
    def __init__(self, gameid, time, home_team, away_team, home_odds, away_odds):
        self.__gameid = gameid
        self.__time = time
        self.__home_team = home_team
        self.__away_team = away_team
        self.__home_odds = home_odds
        self.__away_odds = away_odds
        self.__result = 0

    def get_gameid(self):
        return self.__gameid
    def get_time(self):
        return self.__time
    def get_hometeam(self):
        return self.__home_team
    def get_awayteam(self):
        return self.__away_team
    def get_homeodds(self):
        return self.__home_odds
    def get_awayodds(self):
        return self.__away_odds

    def get_result(self):
        return self.__result
    def change_result(self, result): #1 for home team, 2 for away team, 0 for no result yet
        self.__result = result