#! /usr/bin/env python3
# coding: utf-8

import json
import datetime
from difflib import SequenceMatcher
from collections import OrderedDict

DATA_FILE = 'data/analysis/data.json'
BACKUP_DATA_FILE = 'data/analysis/data.bak.json'
DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M%z'
TIMEZONE = 'Europe/Paris'

SIDES = 'sides'
SIDE_1 = '1'
SIDE_N = 'N'
SIDE_2 = '2'
NAME = 'name'
ODDS = 'odds'
DATETIME = 'datetime'
SCORE = 'score'

MINIMUM_STRING_RATIO = 0.7


def update_data(matches, data):
    now = datetime.datetime.utcnow().strftime(DATE_TIME_FORMAT)
    for match in matches:
        datetime_string = match.datetime.strftime(DATE_TIME_FORMAT)
        summary = '{} {} - {}'.format(datetime_string, match.teams[SIDE_1].name, match.teams[SIDE_2].name)
        print('Registering match: {}'.format(summary))
        match_data = {DATETIME: datetime_string,
                      SIDES: {SIDE_1: {}, SIDE_N: {}, SIDE_2: {}}}
        if summary in data:
            match_data = data[summary]
        for team_id, team in match.teams.items():
            team_data = match_data[SIDES][team_id]
            if NAME not in team_data and team_id != SIDE_N:
                team_data[NAME] = team.name
            if ODDS not in team_data:
                team_data[ODDS] = {}
            for site, odd in team.odds.items():
                if site not in team_data[ODDS]:
                    team_data[ODDS][site] = []
                if not team_data[ODDS][site] or \
                        (now != team_data[ODDS][site][-1][0] and odd != team_data[ODDS][site][-1][1]):
                    team_data[ODDS][site].append([now, odd])
            if team.score:
                team_data[SCORE] = team.score
            match_data[SIDES][team_id] = team_data
        data[summary] = match_data
    return data


def register(matches):
    with open(DATA_FILE) as file:
        data = json.load(file, object_pairs_hook=OrderedDict)
    with open(BACKUP_DATA_FILE, mode='w') as backup:
        json.dump(data, backup)
    update_data(matches, data)
    with open(DATA_FILE, mode='w') as file:
        json.dump(data, file)


def are_strings_similar(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio() > MINIMUM_STRING_RATIO


def enrich_data(matches, data):
    for match in matches:
        match_found = False
        for summary, match_data in data.items():
            if match.datetime == datetime.datetime.strptime(match_data[DATETIME], DATE_TIME_FORMAT) and \
                    (are_strings_similar(match.teams[SIDE_1].name, match_data[SIDES][SIDE_1][NAME]) or
                     are_strings_similar(match.teams[SIDE_2].name, match_data[SIDES][SIDE_2][NAME])):
                match_data[SIDES][SIDE_1][SCORE] = match.teams[SIDE_1].score
                match_data[SIDES][SIDE_2][SCORE] = match.teams[SIDE_2].score
                print('Enriching match: {}'.format(match_data))
                data[summary] = match_data
                match_found = True
                break
        if not match_found:
            print('No match found for: {}'.format(match))


def enrich(matches):
    with open(DATA_FILE) as file:
        data = json.load(file, object_pairs_hook=OrderedDict)
    with open(BACKUP_DATA_FILE, mode='w') as backup:
        json.dump(data, backup)
    enrich_data(matches, data)
    with open(DATA_FILE, mode='w') as file:
        json.dump(data, file)


def get_match_data():
    with open(DATA_FILE) as file:
        return json.load(file, object_pairs_hook=OrderedDict)
