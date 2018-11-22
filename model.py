#! /usr/bin/env python3
# coding: utf-8

import pytz


TIE = 'Tie'
TIMEZONE = 'Europe/Paris'
WEBSITES = ['ZEbet', 'Betclic', 'ParionsWeb', 'Scibet']
MIN_PROB = 0.16
MIN_RETURN = 0.94
MAX_RETURN = 0.96


class Match:

    def __init__(self, match_datetime, team1, team2):
        self.datetime = match_datetime
        self.teams = {'1': Team(team1, None), 'N': Team(TIE, None), '2': Team(team2, None)}
        self.sure_bet = False

    def __str__(self):
        result = "{}: {} vs {}".format(self.datetime.astimezone(pytz.timezone(TIMEZONE)).isoformat(),
                                       self.teams['1'].name, self.teams['2'].name)
        if self.sure_bet:
            result += ' !! SURE BET !!'
        return result

    def __eq__(self, other):
        return isinstance(other, Match) and \
               self.datetime == other.datetime and self.teams == other.teams

    def __ne__(self, other):
        return not self == other


class Team:

    def __init__(self, name, prob):
        self.name = name
        self.prob = prob
        self.score = None
        self.odds = {}

    def get_sub_odds(self):
        sub_odds = {}
        for site, odd in self.odds.items():
            if site in WEBSITES:
                sub_odds[site] = odd
        return sub_odds

    def get_best_odd(self):
        empty_odd = ('', 0.0)
        if self.prob < MIN_PROB:
            return empty_odd
        sub_odds = self.get_sub_odds()
        valid = False
        for site, odd in sub_odds.items():
            if MIN_RETURN < odd * self.prob < MAX_RETURN:
                valid = True
        if valid:
            site_max = max(sub_odds.keys(), key=(lambda k: sub_odds[k]))
            return site_max, sub_odds[site_max]
        return empty_odd

    def __str__(self):
        return '{}: {}'.format(self.name, self.prob)

    def __eq__(self, other):
        return isinstance(other, Team) and \
               self.name == other.name and self.prob == other.prob \
               and self.score == other.score and self.odds == other.odds

    def __ne__(self, other):
        return not self == other


class League:

    def __init__(self, league_id, name):
        self.league_id = league_id
        self.name = name

    def __hash__(self):
        return self.league_id

    def __eq__(self, other):
        return self.league_id == other.league_id

    def __str__(self):
        return self.name
