#! /usr/bin/env python3
# coding: utf-8

import datetime
import locale
import re
import unidecode
import math
import logging

from bs4 import BeautifulSoup
import pytz

from core.common import download
from core.common.model import Match


URL_ROOT = 'http://www.cotes.fr/{}'
BET_FACTOR = 0.5
WEBSITES = ['ZEbet', 'Betclic', 'ParionsWeb', 'Winamax']


def get_matches_with_odds_from_url(url):
    logging.info('Processing league {}'.format(url))
    locale.setlocale(locale.LC_ALL, 'fr')
    paris = pytz.timezone('Europe/Paris')
    matches = []
    page = download.get_page(url)
    soup = BeautifulSoup(page, 'html.parser')
    bettable = soup.find('table', {'class': 'bettable'})
    try:
        for row in bettable.find_all('tr'):
            row_attr = row.attrs
            if 'style' in row_attr:
                teams = row.find_all('a', {'class': 'otn'})
                team1 = unidecode.unidecode(teams[0].string)
                team2 = unidecode.unidecode(teams[1].string)
                subrow = row.find('td', {'class': re.compile('maincol.*')})
                match_text = subrow.get_text()
                regex_match = re.search('(\d* \w* \d{4} à \d{2}h\d{2})', match_text)
                match_time = paris.localize(datetime.datetime.strptime(regex_match.group(0), '%d %B %Y à %Hh%M'))
                sure_bet = 'surebetbox' in subrow.attrs['class']
                match = Match(match_time, team1, team2)
                match.sure_bet = sure_bet
                logging.info('Decoded match: {}'.format(match))
                matches.append(match)
            elif 'class' in row_attr:
                website = row_attr['title'][12:]
                bets = row.find_all('td', {'class': 'bet'})
                odd1 = float(bets[0].string)
                oddx = float(bets[1].string)
                odd2 = float(bets[2].string)
                matches[-1].teams['1'].odds[website] = odd1
                matches[-1].teams['N'].odds[website] = oddx
                matches[-1].teams['2'].odds[website] = odd2
    except ValueError:
        logging.error('Parsing of match failed')
    return matches


def get_matches_with_odds():
    matches = []
    page = download.get_page(URL_ROOT.format('football'))
    soup = BeautifulSoup(page, 'html.parser')
    for league_item in soup.find_all('li', {'class': 'g1'}):
        league_anchor = league_item.find('a', {'href': True})
        url_suffix = unidecode.unidecode(league_anchor['href'])
        matches.extend(get_matches_with_odds_from_url(URL_ROOT.format(url_suffix)))
    return matches


def get_value_bets(params):
    bet_odd_power, min_prob, min_return, max_return = params
    bet_matches = set()
    matches = get_matches_with_odds()
    for match in matches:
        margins = {}
        for site in match.teams['1'].odds.keys():
            margins[site] = 0.0
            for team in match.teams.values():
                margins[site] += 1 / team.odds[site]
        for side_id, side in match.teams.items():
            prob = 0.0
            for site in margins.keys():
                prob += 1 / side.odds[site] / margins[site]
            prob /= len(margins)
            best_website, best_odd = None, 0.0
            for website, odd in side.odds.items():
                if (not WEBSITES or website in WEBSITES) and odd > best_odd:
                    best_odd, best_website = odd, website
            if not best_odd:
                continue
            bet_fraction = BET_FACTOR / math.pow(best_odd, bet_odd_power)
            if prob > min_prob and min_return < prob * best_odd < max_return:
                bet_matches.add((str(match), side_id, best_website, best_odd, match.datetime, bet_fraction))
    return bet_matches
