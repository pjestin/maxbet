#! /usr/bin/env python3
# coding: utf-8

import datetime
import csv
import logging
import json
import unidecode

from core.common import download
from core.common.model import Match, League

MATCHES_URL = 'https://projects.fivethirtyeight.com/soccer-predictions/data.json'
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


def get_matches():
    data = json.loads(download.get_page(MATCHES_URL))
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
        logging.info('Decoded match: {}'.format(match))
        matches.append(match)
    return matches


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
