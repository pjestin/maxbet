#! /usr/bin/env python3
# coding: utf-8

from core.common import download
import json
from core.common.model import Match, League
import datetime
import unidecode
import csv
from collections import OrderedDict

MATCHES_URL = 'https://projects.fivethirtyeight.com/soccer-predictions/data.json'
MATCHES_FILE = 'core/cache/fivethirtyeight/data.json'
MATCHES_CSV_URL = 'https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv'
MATCHES_CSV_FILE = 'core/cache/fivethirtyeight/data.csv'

DATETIME = 'datetime'
DATE = 'date'
LEAGUE_ID = 'league_id'
LEAGUE = 'league'
TEAM1 = 'team1'
TEAM2 = 'team2'
PROB1 = 'prob1'
PROB2 = 'prob2'
PROBTIE = 'probtie'
SCORE1 = 'score1'
SCORE2 = 'score2'
ID = 'id'
LEAGUE_NAME = 'longName'
LEAGUES = 'leagues'
MATCHES = 'matches'

FIVETHIRTYEIGHT = '538'


def get_league_from_id(league_id, data):
    for league_data in data[LEAGUES]:
        if ID in league_data and LEAGUE_NAME in league_data and league_data[ID] == league_id:
            return League(league_id, league_data[LEAGUE_NAME])
    return None


def create_matches(data):
    matches = []
    for match_data in data[MATCHES]:
        match_datetime = datetime.datetime.strptime(match_data[DATETIME], '%Y-%m-%dT%H:%M:%SZ')
        match_datetime = match_datetime.replace(tzinfo=datetime.timezone.utc)
        match = Match(match_datetime, unidecode.unidecode(match_data[TEAM1]),
                      unidecode.unidecode(match_data[TEAM2]))
        match.teams['1'].probs[FIVETHIRTYEIGHT] = float(match_data[PROB1])
        match.teams['N'].probs[FIVETHIRTYEIGHT] = float(match_data[PROBTIE])
        match.teams['2'].probs[FIVETHIRTYEIGHT] = float(match_data[PROB2])
        match.league = get_league_from_id(match_data[LEAGUE_ID], data)
        matches.append(match)
    matches_by_league = OrderedDict()
    for match in matches:
        if match.league not in matches_by_league:
            matches_by_league[match.league] = []
        matches_by_league[match.league].append(match)
    print('Read {} matches under {} leagues'.format(len(matches), len(matches_by_league)))
    return matches_by_league


def create_matches_from_csv():
    matches = []
    download.download_data(MATCHES_CSV_URL, MATCHES_CSV_FILE)
    with open(MATCHES_CSV_FILE, encoding='utf-8', newline='') as file:
        csv_reader = csv.DictReader(file)
        for match_data in csv_reader:
            match_date = datetime.date.strptime(match_data[DATE], '%Y-%m-%d')
            match = Match(match_date, match_data[TEAM1], match_data[TEAM2])
            match.teams['1'].score = match_data[SCORE1]
            match.teams['2'].score = match_data[SCORE2]
            matches.append(match)
    return matches


def read_weekly_matches():
    download.download_data(MATCHES_URL, MATCHES_FILE)
    print('Reading matches data...')
    with open(MATCHES_FILE, encoding='utf-8', newline='') as file:
        data = json.load(file)
        matches = create_matches(data)
    return matches


def get_matches():
    matches = read_weekly_matches().values()
    return [match for sublist in matches for match in sublist]
