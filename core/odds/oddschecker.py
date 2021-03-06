#! /usr/bin/env python3
# coding: utf-8

import locale
import datetime
import logging

from bs4 import BeautifulSoup
import pytz

from core.common import download
from core.common.model import Match


ODDSCHECKER_URL = 'https://www.oddschecker.com'
URL_ROOT = ODDSCHECKER_URL + '/football/{}'


def get_cleaned_odds(websites, odd_list):
    odds = dict(zip(websites, odd_list))
    for website in websites:
        if not odds[website]:
            del odds[website]
    return odds


def decode_match(match_url, home_team_name, away_team_name):
    match_page = download.get_page(match_url)
    if not match_page:
        return None

    match_soup = BeautifulSoup(match_page, 'html.parser')
    bet_table = match_soup.find('table', {'class': 'eventTable'})
    if not bet_table:
        return None

    datetime_string = bet_table['data-time']
    london = pytz.timezone('Europe/London')
    match_datetime = london.localize(datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S'))
    if match_datetime < datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc):
        return None
    match = Match(match_datetime, home_team_name, away_team_name)

    websites = []
    name_to_side_id_map = {home_team_name: '1', 'Draw': 'N', away_team_name: '2'}
    header = bet_table.find('tr', {'class': 'eventTableHeader'})
    for website_anchor in header.find_all('a', {'data-bk': True}):
        websites.append(website_anchor['title'])

    for side in bet_table.find_all('tr', {'class': 'diff-row evTabRow bc'}):
        side_name = side['data-bname']
        if side_name not in name_to_side_id_map:
            continue
        side_id = name_to_side_id_map[side_name]
        odd_list = []
        for odd_tag in side.find_all('td', {'data-odig': True}):
            odd_list.append(float(odd_tag['data-odig']))
        match.teams[side_id].odds = get_cleaned_odds(websites, odd_list)

    logging.info('Decoded match: {}'.format(match))
    return match


def get_matches_with_odds_from_url(league_url):
    logging.info('Processing league {}'.format(league_url))
    league_page = download.get_page(league_url)
    if not league_page:
        return []
    matches = []
    soup = BeautifulSoup(league_page, 'html.parser')
    for row in soup.find_all('tr', {'class': 'match-on'}):
        team_paragraphs = row.find_all('p', {'class': 'fixtures-bet-name beta-footnote'})
        if len(team_paragraphs) != 2:
            continue
        home_team_name = team_paragraphs[0].contents[0]
        away_team_name = team_paragraphs[1].contents[0]
        anchor = row.find('a', {'class': 'beta-callout full-height-link whole-row-link', 'href': True})
        match_url = ODDSCHECKER_URL + ('/' if not anchor['href'].startswith('/') else '') + anchor['href']
        match = decode_match(match_url, home_team_name, away_team_name)
        if match:
            matches.append(match)
    return matches


def get_matches_with_odds():
    locale.setlocale(locale.LC_ALL, 'en')
    matches = []
    page = download.get_page(URL_ROOT.format('leagues-cups'))
    soup = BeautifulSoup(page, 'html.parser')
    league_urls = set()
    for anchor in soup.find_all('a', {'class': 'list-text-indent', 'href': True}):
        league_url = anchor['href']
        if 'http' not in league_url:
            league_url = ODDSCHECKER_URL + '/' + league_url
        league_urls.add(league_url)
    for league_url in league_urls:
        matches.extend(get_matches_with_odds_from_url(league_url))
    return matches
