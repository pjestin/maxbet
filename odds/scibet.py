#! /usr/bin/env python3
# coding: utf-8

from common import download
from bs4 import BeautifulSoup
from common.model import Match
import datetime
import re
import unidecode

URL_ROOT = 'https://www.scibet.com/football/{}'
FILE_PATH_ROOT = 'cache/scibet/league-{}.html'
LEAGUE_URLS = {1818: 'europe/champions-league', 1849: 'netherlands/eredivisie', 1844: 'france/ligue-2',
               2411: 'england/premier-league', 1951: 'united-states/major-league-soccer', 2105: 'brazil/serie-a',
               1882: 'turkey/super-lig', 1845: 'germany/bundesliga-1', 1869: 'spain/primera-division',
               1866: 'russia/1-division', 1843: 'france/ligue-1', 1947: 'japan/j-league', 1846: 'germany/bundesliga-2',
               1859: 'norway/tippeligaen', 1874: 'sweden/allsvenskan', 1871: 'spain/segunda-division',
               1854: 'italy/serie-q', 1975: 'mexico/primera-division', 5641: 'argentina/primera-division',
               1856: 'italy/serie-b', 2417: 'scotland/premier-league', 2412: 'england/championship',
               1832: 'belgium/jupiler-league', 1884: 'greece/superleague', 1879: 'switzerland/super-league',
               1827: 'austria/bundesliga', 1820: 'europe/europa-league', 1864: 'portugal/primeira-liga',
               1837: 'denmark/superligaen', 0: 'ukraine/vyscha-liga', 1: 'poland/ekstraklasa',
               2: 'slovenia/prva-liga', 3: 'wales/premier-league', 4: 'cyprus/first-division',
               5: 'czech-republic/gambrinus-league', 6: 'england/league-cup', 7: 'hungary/otp-bank-liga',
               8: 'romania/liga-1', 9: 'slovakia/super-liga'}
SCIBET = 'Scibet'
STYLE_PATTERN = '.*width:(\d*.?\d*)%.*'


def get_matches_from_file(file_path):
    matches = []
    with open(file_path, encoding='latin_1') as file:
        soup = BeautifulSoup(file, 'html.parser')
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
            matches.append(match)
    return matches


def get_matches_for_league(league_id):
    print('Processing league {}'.format(league_id))
    if league_id not in LEAGUE_URLS:
        print('Unrecognized league: {}'.format(league_id))
        return
    url = URL_ROOT.format(LEAGUE_URLS[league_id])
    file_path = FILE_PATH_ROOT.format(league_id)
    download.download_data(url, file_path)
    return get_matches_from_file(file_path)


def get_matches_by_league():
    matches_by_league = {}
    for league_id in LEAGUE_URLS:
        matches = get_matches_for_league(league_id)
        matches_by_league[league_id] = matches
    return matches_by_league


def get_matches():
    matches = get_matches_by_league().values()
    return [match for sublist in matches for match in sublist]
