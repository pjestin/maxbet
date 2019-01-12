#! /usr/bin/env python3
# coding: utf-8

import json
import datetime
from difflib import SequenceMatcher
from collections import OrderedDict

DATA_FILE = 'core/analysis/data/db.json'
BACKUP_DATA_FILE = 'core/analysis/data/db.bak.json'
DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M%z'
TIMEZONE = 'Europe/Paris'

SIDES = 'sides'
SIDE_1 = '1'
SIDE_N = 'N'
SIDE_2 = '2'
NAME = 'name'
ODDS = 'odds'
PROBS = 'probs'
DATETIME = 'datetime'
SCORE = 'score'

MINIMUM_STRING_RATIO = 0.7


def are_strings_similar(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio() > MINIMUM_STRING_RATIO


def is_match(match, match_data):
    return match.datetime == datetime.datetime.strptime(match_data[DATETIME], DATE_TIME_FORMAT) and \
           (are_strings_similar(match.teams[SIDE_1].name, match_data[SIDES][SIDE_1][NAME]) or
            are_strings_similar(match.teams[SIDE_2].name, match_data[SIDES][SIDE_2][NAME]))


def register_numbers_at_time(team_numbers, team_data_numbers, now):
    for site, odd in team_numbers.items():
        if not odd:
            continue
        if site not in team_data_numbers:
            team_data_numbers[site] = []
        if not team_data_numbers[site] or \
                (now != team_data_numbers[site][-1][0] and odd != team_data_numbers[site][-1][1]):
            team_data_numbers[site].append([now, odd])


def update_match_data(match, match_data, now):
    for team_id, team in match.teams.items():
        team_data = match_data[SIDES][team_id]
        if NAME not in team_data and team_id != SIDE_N:
            team_data[NAME] = team.name
        if team.odds:
            if ODDS not in team_data:
                team_data[ODDS] = {}
            register_numbers_at_time(team.odds, team_data[ODDS], now)
        if team.probs:
            if PROBS not in team_data:
                team_data[PROBS] = {}
            register_numbers_at_time(team.probs, team_data[PROBS], now)
        if team.score is not None:
            team_data[SCORE] = team.score


def enrich_data(matches, data):
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).strftime(DATE_TIME_FORMAT)
    for match in matches:
        datetime_string = match.datetime.strftime(DATE_TIME_FORMAT)
        this_match_data = {DATETIME: datetime_string, SIDES: {SIDE_1: {}, SIDE_N: {}, SIDE_2: {}}}
        this_summary = '{} {} - {}'.format(datetime_string, match.teams[SIDE_1].name, match.teams[SIDE_2].name)
        for summary, match_data in data.items():
            if is_match(match, match_data):
                this_match_data = match_data
                this_summary = summary
                break
        print('Updating match: {}'.format(this_summary))
        update_match_data(match, this_match_data, now)
        data[this_summary] = this_match_data


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


def get_finished_match_data():
    match_data = get_match_data()
    finished_match_data = {}
    for summary, match in match_data.items():
        if SIDES in match and SIDE_1 in match[SIDES] and SIDE_2 in match[SIDES]\
                and SCORE in match[SIDES][SIDE_1] and SCORE in match[SIDES][SIDE_2]:
            finished_match_data[summary] = match
    return OrderedDict(sorted(finished_match_data.items()))


def remove_late_odds(data):
    for summary, match_data in data.items():
        match_datetime = datetime.datetime.strptime(match_data[DATETIME], DATE_TIME_FORMAT)
        for team_id in ['1', 'N', '2']:
            team_data = match_data[SIDES][team_id]

            for number_id in [ODDS, PROBS]:
                if number_id in team_data:
                    for website, numbers in team_data[number_id].items():
                        numbers_without_late = []
                        for number_datetime_string, number in numbers:
                            number_datetime = datetime.datetime.strptime(number_datetime_string, DATE_TIME_FORMAT)
                            if number_datetime < match_datetime:
                                numbers_without_late.append([number_datetime_string, number])
                            else:
                                print('Removing match number for match {}'.format(summary))
                        team_data[number_id][website] = numbers_without_late

        match_data[SIDES][team_id] = team_data
    data[summary] = match_data


def add_bet_time_zone(data):
    for summary, match_data in data.items():
        for team_id in ['1', 'N', '2']:
            team_data = match_data[SIDES][team_id]

            for number_id in [ODDS, PROBS]:
                if number_id in team_data:
                    for website, numbers in team_data[number_id].items():
                        numbers_with_time_zones = []
                        for number_datetime_string, number in numbers:
                            if len(number_datetime_string) == 16:
                                number_datetime = datetime.datetime.strptime(number_datetime_string, '%Y-%m-%dT%H:%M')
                                number_datetime = number_datetime.replace(tzinfo=datetime.timezone.utc)
                                number_datetime_string = number_datetime.strftime(DATE_TIME_FORMAT)
                                print('Adding timezone {}'.format(number_datetime_string))
                            numbers_with_time_zones.append([number_datetime_string, number])
                        team_data[number_id][website] = numbers_with_time_zones

        match_data[SIDES][team_id] = team_data
    data[summary] = match_data


def patch():
    with open(DATA_FILE) as file:
        data = json.load(file, object_pairs_hook=OrderedDict)
    with open(BACKUP_DATA_FILE, mode='w') as backup:
        json.dump(data, backup)
    remove_late_odds(data)
    with open(DATA_FILE, mode='w') as file:
        json.dump(data, file)
