#! /usr/bin/env python3
# coding: utf-8

from core.common import download
from bs4 import BeautifulSoup
from core.common.model import Match
import datetime
import re
import unidecode

URL_FOOTBALL = 'https://www.scibet.com/football'
SCIBET = 'Scibet'
STYLE_PATTERN = '.*width:(\d*.?\d*)%.*'


def get_matches_from_url(url):
    print('Processing league: {}'.format(url))
    matches = []
    page = download.get_page(url)
    soup = BeautifulSoup(page, 'html.parser')
    bettable = soup.find('table')
    for row in bettable.find_all('tr'):
        odds = []
        match_datetime = None
        for span in row.find_all('span'):
            if span.has_attr('data-date'):
                datetime_field = span.attrs['data-date']
                match_datetime = datetime.datetime.fromtimestamp(int(datetime_field),
                                                                 tz=datetime.timezone.utc)
            elif span.has_attr('data-odds'):
                odds.append(float(span.attrs['data-odds']))
        team1 = unidecode.unidecode(row.find('td', {'class': 'tar'}).a.string)
        team2 = unidecode.unidecode(row.find('td', {'class': 'tal'}).a.string)
        match = Match(match_datetime, team1, team2)
        if row.find('span', {'title': 'Finished'}):
            score = row.find('td', {'style': 'width:6%'}).a.strong.string
            score_reg = re.match('(\d*) - (\d*)', score)
            score1 = int(score_reg.group(1))
            score2 = int(score_reg.group(2))
            match.teams['1'].score = score1
            match.teams['2'].score = score2
        else:
            probs = []
            if row.find('div', {'class': 'bar bar-success'}):
                probs.append(re.match(STYLE_PATTERN, row.find('div', {'class': 'bar bar-success'}).attrs['style']))
            if row.find('div', {'class': 'bar bar-success'}):
                probs.append(re.match(STYLE_PATTERN, row.find('div', {'class': 'bar bar-warning'}).attrs['style']))
            if row.find('div', {'class': 'bar bar-success'}):
                probs.append(re.match(STYLE_PATTERN, row.find('div', {'class': 'bar bar-danger'}).attrs['style']))
            i = 0
            for side in ['1', 'N', '2']:
                if len(odds) == 3:
                    match.teams[side].odds[SCIBET] = odds[i]
                if len(probs) == 3 and probs[i]:
                    match.teams[side].probs[SCIBET] = float(probs[i].group(1)) / 100.0
                i += 1
        print('Decoded match: {}'.format(match))
        matches.append(match)
    return matches


def get_matches():
    matches = []
    football_page = download.get_page(URL_FOOTBALL)
    soup = BeautifulSoup(football_page, 'html.parser')
    navigation = soup.find('ul', {'class': 'navigation'})
    openable_active = navigation.find('li', {'class': 'openable active open'})
    for league_item in openable_active.find_all('ul'):
        if league_item.find('li', {'class': 'openable'}):
            continue
        league_anchor = league_item.find('a', {'href': True, 'title': True})
        league_url = league_anchor['href']
        matches.extend(get_matches_from_url(league_url))
    return matches
