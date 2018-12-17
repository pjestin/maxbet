#! /usr/bin/env python3
# coding: utf-8

from core.common import download
from core.common.model import Match
from bs4 import BeautifulSoup
import locale
from datetime import datetime, timezone
import re


ODDSCHECKER_URL = 'https://www.oddschecker.com'
URL_ROOT = ODDSCHECKER_URL + '/football/{}'
FILE_PATH_ROOT = 'core/cache/oddschecker/league-{}.html'
FILE_PATH_PER_MATCH_ROOT = 'core/cache/oddschecker/{}.html'
LEAGUE_URLS = {2411: 'english/premier-league'}


def get_matches_with_odds_from_file(file_path):
    locale.setlocale(locale.LC_ALL, 'en_GB')
    matches = []
    with open(file_path, encoding='latin_1', newline='') as file:
        soup = BeautifulSoup(file, 'html.parser')
        for anchor in soup.find_all('a', {'class': 'beta-callout full-height-link whole-row-link', 'href': True}):
            url = ODDSCHECKER_URL + anchor['href']
            match_url = anchor['href'].split('/')[-2]
            match_file_path = FILE_PATH_PER_MATCH_ROOT.format(match_url)
            download.download_data(url, match_file_path)
            with open(match_file_path, encoding='latin_1', newline='') as match_file:
                match_soup = BeautifulSoup(match_file, 'html.parser')

                bet_table = match_soup.find('table', {'class': 'eventTable'})
                datetime_string = bet_table['data-time']
                match_datetime = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)

                title = match_soup.find('h1', {'class': 'beta-h2'}).string
                title_match = re.match('(.*) v (.*) Winner Betting Odds', title)
                name_to_side_id_map = {title_match.group(1): '1', 'Draw': 'N', title_match.group(2): '2'}
                match = Match(match_datetime, title_match.group(1), title_match.group(2))

                websites = []
                header = bet_table.find('tr', {'class': 'eventTableHeader'})
                for website_anchor in header.find_all('a', {'data-bk': True}):
                    websites.append(website_anchor['title'])

                for side in bet_table.find_all('tr', {'class': 'diff-row evTabRow bc'}):
                    side_name = side['data-bname']
                    side_id = name_to_side_id_map[side_name]
                    odd_list = []
                    for odd_tag in side.find_all('td', {'data-odig': True}):
                        odd_list.append(float(odd_tag['data-odig']))
                    match.teams[side_id].odds = dict(zip(websites, odd_list))

                matches.append(match)

    return matches


def get_matches_with_odds_for_league(league_id):
    print('Processing league {}'.format(league_id))
    if league_id not in LEAGUE_URLS:
        print('Unrecognized league: {}'.format(league_id))
        return
    url = URL_ROOT.format(LEAGUE_URLS[league_id])
    file_path = FILE_PATH_ROOT.format(league_id)
    download.download_data(url, file_path)
    return get_matches_with_odds_from_file(file_path)


def get_matches_with_odds():
    matches = []
    for league_id in LEAGUE_URLS:
        matches.extend(get_matches_with_odds_for_league(league_id))
    return matches
